# -*- coding: utf-8 -*-
"""Fetch metadata from plugins and dump it to temporary JSON file.

This fetches metadata from plugins defined using different build systems
 * setuptools/pip: setup.json
 * poetry: pyproject.toml
 * flit: pyproject.toml
"""
import ast
import json
import os
import sys
import traceback
import urllib
from collections import OrderedDict
# pylint: disable=missing-function-docstring
from configparser import ConfigParser
from typing import List, Optional

import requests
import requests_cache
import requirements
import tomlkit
from tomlkit.toml_document import TOMLDocument

from . import (PLUGINS_FILE_ABS, PLUGINS_METADATA, PLUGINS_METADATA_KEYS,
               classifier_to_status, status_dict)

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


def parse_plugin_info(url: str, content: Optional[str]) -> dict:  # pylint: disable=too-many-return-statements
    """Fetches plugin metadata in different formats.

    - pyproject.toml (for poetry/flit)
    - setup.cfg (for setuptools)
    - setup.json (for setuptools)

    This returns the keys:
     * entry_points
     * metadata
     * aiida_version

    """
    default_infos = {
        'entry_points': {},
        'metadata': None,
        'aiida_version': None,
    }

    if content is None:
        return default_infos

    if 'pyproject.toml' in url:
        try:
            pyproject = tomlkit.parse(content)
        except tomlkit.exceptions.TOMLKitError as exc:
            report(f'  > WARNING! Unable to parse TOML: {exc}')
            return default_infos

        tool_name = pyproject.get('tool', '')

        if 'poetry' in tool_name:
            return parse_poetry(pyproject)
        if 'flit' in tool_name:
            return parse_flit_old(pyproject)

        report(
            f'  > WARNING! Unknown build system in pyproject.toml: {tool_name}'
        )
        return default_infos

    if 'setup.cfg' in url:
        try:
            config = ConfigParser()
            config.read_string(content)
        except Exception as exc:  # pylint: disable=broad-except
            report(f'  > WARNING! Unable to parse setup.cfg: {exc}')
            return default_infos
        return parse_setup_cfg(config)

    try:
        data = json.loads(content)
    except ValueError as exc:
        report(f'  > WARNING! Unable to parse JSON: {exc}')
        return default_infos

    return parse_setup_json(data)


def parse_setup_json(data: dict) -> dict:
    """Parse setup.json."""
    infos = {
        'aiida_version':
        get_aiida_version_list(data.get('install_requires', [])),
        'metadata':
        {k: data[k] if k in data else ''
         for k in PLUGINS_METADATA_KEYS},
        'entry_points': data.get('entry_points', {}).copy(),
    }
    infos['metadata']['classifiers'] = data.get('classifiers', [])

    return infos


def parse_poetry(data: TOMLDocument) -> dict:
    """Parse poetry pyproject.toml."""
    infos = {
        'aiida_version': get_aiida_version_poetry(data),
        'metadata': {
            # all the following fields are mandatory in Poetry
            'version':
            str(data['tool']['poetry']['version']),
            'description':
            str(data['tool']['poetry']['description']),
            # the authors is a list of the strings of the form "name <email>"
            'author':
            ', '.join(
                a.split('<')[0].strip()
                for a in data['tool']['poetry']['authors']),
        },
        'entry_points': {
            group: ['{} = {}'.format(k, v) for k, v in entries.items()]
            for group, entries in data['tool']['poetry'].get('plugins',
                                                             {}).items()
        }
    }
    infos['metadata']['classifiers'] = [
        str(item) for item in data['tool']['poetry'].get('classifiers', [])
    ]
    return infos


def parse_flit_old(data: TOMLDocument) -> dict:
    """Parse flit pyproject.toml with old-style metadata."""
    # uses https://flit.readthedocs.io/en/latest/pyproject_toml.html#old-style-metadata

    # version is not part of the metadata but expected to available in <module>/__init__.py:__version__
    # description is available as a reference in `description-file` (requires another fetch)
    # author is a mandatory field in Flit
    report('  > WARNING! version & description metadata'
           ' are not (yet) parsed from the Flit buildsystem pyproject.toml')
    metadata = data['tool']['flit'].get('metadata', {})
    return {
        'aiida_version': get_aiida_version_list(metadata.get('requires', [])),
        'metadata': {
            'author': str(metadata.get('author', '')),
            'version': '',
            'description': '',
        },
        'entry_points': {
            group: [f'{k} = {v}' for k, v in entries.items()]
            for group, entries in data['tool']['flit'].get('entrypoints',
                                                           {}).items()
        }
    }


def parse_setup_cfg(config: ConfigParser) -> dict:
    """Parse setup.cfg."""
    infos = {
        'aiida_version':
        get_aiida_version_list(
            config.get('options', 'install_requires').splitlines() if config.
            has_option('options', 'install_requires') else []),
        'metadata': {
            k: (config.get('metadata', k)
                if config.has_option('metadata', k) else '')
            for k in PLUGINS_METADATA_KEYS
        },
        'entry_points': {}
    }
    if config.has_section('options.entry_points'):
        for name, content in config.items('options.entry_points'):
            infos['entry_points'][name] = [
                l.strip() for l in content.splitlines()
                if l.strip() and not l.strip().startswith('#')
            ]
    if config.has_option('metadata', 'classifiers'):
        infos['metadata']['classifiers'] = [
            l.strip()
            for l in config.get('metadata', 'classifiers').splitlines()
            if l.strip() and not l.strip().startswith('#')
        ]

    return infos


def get_aiida_version_list(install_requires: List[str]) -> Optional[str]:
    """Get AiiDA version that this plugin is compatible with."""
    try:
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
    from poetry.semver import \
        parse_constraint  # pylint: disable=import-outside-toplevel

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


def get_version_from_module(content: str) -> Optional[str]:
    """Get the __version__ value from a module."""
    # adapted from setuptools/config.py
    try:
        module = ast.parse(content)
    except SyntaxError as exc:
        report(f'  > WARNING! Unable to parse module: {exc}')
        return None
    try:
        return next(
            ast.literal_eval(statement.value) for statement in module.body
            if isinstance(statement, ast.Assign)
            for target in statement.targets
            if isinstance(target, ast.Name) and target.id == '__version__')
    except StopIteration:
        return None


def fetch_file(file_url: str, file_type: str = 'plugin info') -> str:
    """Fetch plugin info from a URL to a file."""
    try:
        response = requests.get(file_url)
        # raise an exception for all 4xx/5xx errors
        response.raise_for_status()
    except Exception:  # pylint: disable=broad-except
        report(f'  > WARNING! Unable to retrieve {file_type} from: {file_url}')
        report(traceback.format_exc())
        return None
    return response.content.decode(response.encoding or 'utf8')


def complete_plugin_data(plugin_data: dict):
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
    plugin_info_url = plugin_data.pop('plugin_info', None)
    if plugin_info_url is None:
        report('  > WARNING: Missing plugin_info key!')
        plugin_info_content = None
    else:
        plugin_info_content = fetch_file(plugin_info_url)

    plugin_info = parse_plugin_info(plugin_info_url, plugin_info_content)

    # setuptools and flit can read the version from the package
    if 'version_file' in plugin_data and (
            not plugin_info['metadata'].get('version', None)
            or str(plugin_info['metadata']['version']).startswith('attr:')):
        content = fetch_file(plugin_data.pop('version_file'))
        if content is not None:
            version = get_version_from_module(content)
            if version is not None:
                plugin_info['metadata']['version'] = version

    plugin_data['hosted_on'] = get_hosted_on(plugin_data['code_home'])

    plugin_data.update(plugin_info)

    validate_dev_status(plugin_data)

    if 'documentation_url' in plugin_data:
        validate_doc_url(plugin_data['documentation_url'])

    validate_plugin_entry_points(plugin_data)

    if 'WARNING' in '\n'.join(PLUGIN_LOG):
        LOG += PLUGIN_LOG
    PLUGIN_LOG = []

    return plugin_data


def validate_dev_status(plugin_data: dict):
    """Validate the development_status key, potentially sourcing from classifiers."""
    classifiers = plugin_data['metadata'].get(
        'classifiers', []) if plugin_data.get('metadata', None) else []
    if plugin_data['metadata'] and 'Framework :: AiiDA' not in classifiers:
        report("  > WARNING: Missing classifier 'Framework :: AiiDA'")

    development_status = None
    for classifier in classifiers:
        if classifier in classifier_to_status:
            if development_status is not None:
                report(
                    '  > WARNING: Multiple development statuses found in classifiers'
                )
            development_status = classifier_to_status[classifier]

    if development_status and 'development_status' in plugin_data and (
            development_status != plugin_data['development_status']):
        report(
            f'  > WARNING: Development status in classifiers ({development_status}) '
            f"does not match development_status in metadata ({plugin_data['development_status']})"
        )

    # prioritise development_status from plugins.json
    if 'development_status' not in plugin_data:
        plugin_data['development_status'] = development_status

    # note: for more validation, it might be sensible to switch to voluptuous
    if plugin_data['development_status'] not in list(status_dict.keys()):
        report("  > WARNING: Invalid state '{}'".format(
            plugin_data['development_status']))


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
        plugins_raw_data: dict = json.load(handle)

    plugins_metadata = OrderedDict()

    for plugin_name, plugin_data in sorted(plugins_raw_data.items()):
        plugin_data['name'] = plugin_name
        plugins_metadata[plugin_name] = complete_plugin_data(plugin_data)

    with open(PLUGINS_METADATA, 'w') as handle:
        json.dump(plugins_metadata, handle, indent=2)
    report('  - {} dumped'.format(PLUGINS_METADATA))

    if GITHUB_ACTIONS:
        print('::set-output name=error::' + '%0A'.join(LOG))
