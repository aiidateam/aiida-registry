# -*- coding: utf-8 -*-
"""Fetch metadata from plugins and dump it to temporary JSON file.

This fetches metadata from plugins defined using different build systems
 * setuptools/pip: setup.json
 * poetry: pyproject.toml
 * flit: pyproject.toml
"""
# pylint: disable=missing-function-docstring

import urllib
import json
import os
import sys
import traceback
from collections import OrderedDict
import six

import requests
import requests_cache
import tomlkit
from . import PLUGINS_METADATA, PLUGINS_FILE_ABS, status_dict, PLUGINS_METADATA_KEYS

if os.environ.get('CACHE_REQUESTS'):
    # Set environment variable CACHE_REQUESTS to cache requests for 1 day for faster testing
    # e.g.: export CACHE_REQUESTS=1
    requests_cache.install_cache('demo_cache', expire_after=60 * 60 * 24)

GITHUB_ACTIONS = os.environ.get('GITHUB_ACTIONS') == 'true'
LOG = []  # global log messages
PLUGIN_LOG = []  # per-plugin log messages


def report(string):
    """Write to stdout and log.

    Used to display log in  actions.
    """
    if GITHUB_ACTIONS:
        # Set the step ouput error message which can be used, e.g., for display as part of an issue comment.
        PLUGIN_LOG.append(string)
    print(string)


def get_hosted_on(url):
    try:
        requests.get(url, timeout=30)
    except Exception:
        raise ValueError("Unable to open 'code_home' url: '{}'".format(url))

    netloc = urllib.parse.urlparse(url).netloc

    # Remove port (if any)
    netloc = netloc.partition(':')[0]

    # Remove subdomains (this only works for domain suffixes of length 1!)
    # TODO: fix it for domains like yyy.co.uk  # pylint: disable=fixme
    netloc = '.'.join(netloc.split('.')[-2:])

    return netloc


def fetch_plugin_info(url):
    """Fetches plugin metadata in different formats.

    setup.json (for pip/setuptools)
    pyproject.toml (for poetry/flit)
    """
    try:
        response = requests.get(url)
        response.raise_for_status(
        )  # raise an exception for all 4xx/5xx errors
    except Exception:  # pylint: disable=broad-except
        report(
            '  > WARNING! Unable to retrieve plugin info from: {}'.format(url))
        report(traceback.format_exc())
        return None

    if 'pyproject.toml' in url:
        try:
            pyproject = tomlkit.parse(response.content)
        except tomlkit.exceptions.TOMLKitError:
            report('  > WARNING! Unable to parse TOML')

        for buildsystem in ('poetry', 'flit'):
            if buildsystem in pyproject['tool']:
                return (buildsystem, pyproject)
        report('  > WARNING! Unknown build system in pyproject.toml')
    else:
        try:
            return ('setuptools', json.loads(response.content))
        except ValueError:
            report('  > WARNING! Unable to parse JSON')

    return None


def get_aiida_version_setup_json(setup_json):
    """Get AiiDA version that this plugin is compatible with.
    """
    import requirements  # pylint: disable=import-outside-toplevel

    try:
        install_requires = setup_json['install_requires']
        reqs = requirements.parse('\n'.join(install_requires))

        aiida_specs = []
        for req in reqs:
            # note: this also catches aiida-core[extra1]
            if req.name in ['aiida-core', 'aiida_core', 'aiida']:
                aiida_specs += req.specs

        if not aiida_specs:
            report('  > WARNING! AiiDA version not specified')
            return None

        # precedence of version specs, from high to low
        precedence = ['==', '>=', '>', '<=', '<']
        sort_order = {precedence[i]: i for i in range(len(precedence))}
        aiida_specs = sorted(aiida_specs,
                             key=lambda r: sort_order.get(r[0], 10))

        # first index: operator (e,g, '>=')
        # second index: version (e.g. '0.12.0rc2')
        # In the future, this can be used to e.g. display a banner for 1.0-compatible plugins
        return ','.join([s[0] + s[1] for s in aiida_specs])

    except KeyError:
        return None


def get_aiida_version_poetry(pyproject):
    """Get AiiDA version that this plugin is compatible with from a pyproject.toml.
    """
    from poetry.semver import parse_constraint  # pylint: disable=import-outside-toplevel

    try:
        deps = pyproject['tool']['poetry']['dependencies']
    except KeyError:
        return None

    for name, data in deps.items():
        if name not in ['aiida-core', 'aiida_core', 'aiida']:
            continue

        try:  # data is either a dict {"version": ..., "extras": ["..", ], }
            version = data['version']
        except TypeError:  # or directly the version string
            version = data

        break
    else:
        report('  > WARNING! AiiDA version not specified')
        return None

    try:
        return str(parse_constraint(version))
    except ValueError:
        report(
            '  > WARNING: Invalid version encountered in Poetry pyproject.toml for aiida-core'
        )

    return None


def get_plugin_info(plugin_info):
    """Fetch metadata from plugin_info url.

    This adds the keys:
     * entry_points
     * metadata
     * aiida_version

     """
    infos = {
        'entry_points': {},
        'metadata': None,
        'aiida_version': None,
    }

    if plugin_info is None:
        return infos

    buildsystem, data = plugin_info

    if buildsystem not in ['setuptools', 'poetry', 'flit']:
        report("  > WARNING! build system '{}' is not supported".format(
            buildsystem))
        return infos

    try:
        if buildsystem == 'setuptools':
            infos['entry_points'].update(
                data['entry_points'])  # updating it gives us a copy
        elif buildsystem == 'poetry':
            infos['entry_points'].update({
                group: ['{} = {}'.format(k, v) for k, v in entries.items()]
                for group, entries in data['tool']['poetry']
                ['plugins'].items()
            })
        elif buildsystem == 'flit':
            infos['entry_points'].update({
                group: ['{} = {}'.format(k, v) for k, v in entries.items()]
                for group, entries in data['tool']['flit']
                ['entrypoints'].items()
            })
    except KeyError:
        pass

    if buildsystem == 'setuptools':
        infos['metadata'] = {
            k: data[k] if k in data else ''
            for k in PLUGINS_METADATA_KEYS
        }

        # pylint: disable=unsupported-assignment-operation
        infos['aiida_version'] = get_aiida_version_setup_json(data)
        infos['metadata']['classifiers'] = data[
            'classifiers'] if 'classifiers' in data else []

        if 'Framework :: AiiDA' not in infos['metadata']['classifiers']:  # pylint: disable=unsubscriptable-object
            report("  > WARNING: Missing classifier 'Framework :: AiiDA'")

    elif buildsystem == 'poetry':
        # all the following fields are mandatory in Poetry
        infos['metadata'] = {
            'version':
            data['tool']['poetry']['version'],
            'description':
            data['tool']['poetry']['description'],
            # the authors is a list of the strings of the form "name <email>"
            'author':
            ', '.join(
                a.split('<')[0].strip()
                for a in data['tool']['poetry']['authors']),
        }
        infos['aiida_version'] = get_aiida_version_poetry(data)
    elif buildsystem == 'flit':
        # version is not part of the metadata but expected to available in <module>/__init__.py:__version__
        # description is available as a reference in `description-file` (requires another fetch)
        # author is a mandatory field in Flit
        infos['metadata'] = {
            'author': data['tool']['flit']['metadata']['author'],
            'version': '',
            'description': '',
        }
        report(
            '  > WARNING! version & description metadata and AiiDA version'
            ' are not (yet) parsed from the Flit buildsystem pyproject.toml')

    return infos


def complete_plugin_data(plugin_data):
    """Update plugin data dictionary.

      * add metadata, aiida_version and entrypoints from plugin_info
      * add package_name if missing
      * add hosted_on
      & more
     used for rendering."""
    global LOG, PLUGIN_LOG  # pylint:disable=global-statement

    if 'package_name' not in list(plugin_data.keys()):
        plugin_data['package_name'] = plugin_data['name'].replace('-', '_')

    report(f'  - {plugin_data["package_name"]}')

    # Get link to setup.json file (set to None if not retrievable)
    try:
        plugin_info_link = plugin_data['plugin_info']
    except KeyError:
        report('  > WARNING: Missing plugin_info key!')
        plugin_data['plugin_info'] = None
    else:
        plugin_data['plugin_info'] = fetch_plugin_info(plugin_info_link)

    plugin_data['hosted_on'] = get_hosted_on(plugin_data['code_home'])

    plugin_data.update(get_plugin_info(plugin_data['plugin_info']))

    # note: for more validation, it might be sensible to switch to voluptuous
    if plugin_data['development_status'] not in list(status_dict.keys()):
        report("  > WARNING: Invalid state '{}'".format(
            plugin_data['development_status']))

    if 'documentation_url' in plugin_data:
        validate_doc_url(plugin_data['documentation_url'])

    validate_plugin_entry_points(plugin_data)

    if 'WARNING' in '\n'.join(PLUGIN_LOG):
        LOG += PLUGIN_LOG
    PLUGIN_LOG = []

    return plugin_data


def validate_doc_url(url):
    """Validate that documentation URL provides valid HTTP response."""
    try:
        response = requests.get(url)
        response.raise_for_status(
        )  # raise an exception for all 4xx/5xx errors
    except Exception:  # pylint: disable=broad-except
        report(
            '  > WARNING! Unable to reach documentation URL: {}'.format(url))
        report(traceback.print_exc(file=sys.stdout))


def validate_plugin_entry_points(plugin_data):
    """Validate that all entry points registered by the plugin start with the registered entry point root."""

    if 'entry_point_prefix' in plugin_data:
        entry_point_root = plugin_data['entry_point_prefix']
        if not 'aiida_' + plugin_data['entry_point_prefix'].lower(
        ) == plugin_data['package_name'].lower():
            report(
                f"  > WARNING: Prefix \'{plugin_data['entry_point_prefix']}\' does not follow naming convention."
            )
    else:
        # plugin should not specify any entry points
        entry_point_root = 'MISSING'

    for ept_group, ept_list in plugin_data['entry_points'].items():
        # we only restrict aiida's entry point groups
        if not ept_group.startswith('aiida.'):
            continue
        for ept in ept_list:
            ept_string, _path = ept.split('=')
            ept_string = ept_string.strip()
            if not ept_string.startswith(entry_point_root):
                report(
                    f"  > WARNING: Entry point '{ept_string}' does not start with prefix '{entry_point_root}.'"
                )


def fetch_metadata():

    with open(PLUGINS_FILE_ABS) as handle:
        plugins_raw_data = json.load(handle)

    plugins_metadata = OrderedDict()

    for plugin_name, plugin_data in sorted(six.iteritems(plugins_raw_data)):
        plugins_metadata[plugin_name] = complete_plugin_data(plugin_data)

    with open(PLUGINS_METADATA, 'w') as handle:
        json.dump(plugins_metadata, handle, indent=2)
    report('  - {} dumped'.format(PLUGINS_METADATA))

    if GITHUB_ACTIONS:
        print('::set-output name=error::' + '%0A'.join(LOG))
