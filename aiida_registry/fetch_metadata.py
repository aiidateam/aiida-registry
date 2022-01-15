# -*- coding: utf-8 -*-
"""Fetch metadata from plugins and dump it to temporary JSON file.

Data is primarily sourced from PyPI,
with a fallback to the repository build file (setup.json, setup.cfg, pyproject.toml).

Currently the entry points are always read from the build,
since PyPI JSON does not include entry points,
and so we would need to download and read the wheel file.
"""
import json
import os
import sys
import traceback
import urllib
from collections import OrderedDict

import requests
import requests_cache
from poetry.core.version.requirements import Requirement

from . import (PLUGINS_FILE_ABS, PLUGINS_METADATA, REPORTER,
               classifier_to_status, status_dict)
from .parse_build_file import get_data_parser, identify_build_tool

if os.environ.get('CACHE_REQUESTS'):
    # Set environment variable CACHE_REQUESTS to cache requests for 1 day for faster testing
    # e.g.: export CACHE_REQUESTS=1
    requests_cache.install_cache('demo_cache', expire_after=60 * 60 * 24)


def get_hosted_on(url):
    """Get the hosting service from a URL."""
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


def fetch_file(file_url: str,
               file_type: str = 'plugin info',
               warn=True) -> str:
    """Fetch plugin info from a URL to a file."""
    try:
        response = requests.get(file_url)
        # raise an exception for all 4xx/5xx errors
        response.raise_for_status()
    except Exception:  # pylint: disable=broad-except
        if warn:
            REPORTER.warn(
                f'  > WARNING! Unable to retrieve {file_type} from: {file_url}'
            )
            REPORTER.debug(traceback.format_exc())
        return None
    return response.content.decode(response.encoding or 'utf8')


def complete_plugin_data(plugin_data: dict):  # pylint: disable=too-many-branches,too-many-statements
    """Update plugin data dictionary.

      * add metadata, aiida_version and entrypoints from plugin_info
      * add package_name if missing
      * add hosted_on
      & more
     used for rendering.
    """
    if 'package_name' not in list(plugin_data.keys()):
        plugin_data['package_name'] = plugin_data['name'].replace('-', '_')

    REPORTER.info(f'{plugin_data["package_name"]}')

    plugin_data['hosted_on'] = get_hosted_on(plugin_data['code_home'])
    plugin_data.update({
        'metadata': {},
        'aiida_version': None,
        'entry_points': {},
    })

    # first try to get metadata from PyPI
    pypi_info = None
    missing_pypi_requires = False
    if 'pypi_name' in plugin_data:
        pypi_info = fetch_file(
            f"https://pypi.org/pypi/{plugin_data['pypi_name']}/json")
        if pypi_info is not None:
            pypi_data = json.loads(pypi_info)
            # check if both a wheel and sdist are available
            build_types = [
                data['packagetype'] for data in pypi_data.get('urls') or []
                if data.get('packagetype')
            ]
            if 'sdist' not in build_types:
                REPORTER.warn('No sdist available for PyPI release')
            if 'bdist_wheel' not in build_types:
                REPORTER.warn('No bdist_wheel available for PyPI release')
            plugin_data['pypi_builds'] = build_types

            # get data from pypi JSON
            pypi_info_data = pypi_data.get('info', {})

            # add required metadata
            for key_from, key_to in (
                ('summary', 'description'),
                ('author', 'author'),
                ('author_email', 'author_email'),
                ('license', 'license'),
                ('home_page', 'home_page'),
                ('classifiers', 'classifiers'),
                ('version', 'version'),
            ):
                if pypi_info_data.get(key_from):
                    plugin_data['metadata'][key_to] = pypi_info_data[key_from]

            # find aiida-version
            # note if a bdist_wheel is not available,
            # then requires_dist will likely not be available
            if pypi_info_data.get('requires_dist'):
                for req in pypi_info_data['requires_dist']:
                    try:
                        parsed = Requirement(req)
                    except Exception:  # pylint: disable=broad-except
                        continue
                    if parsed.name in ['aiida-core', 'aiida_core', 'aiida']:
                        plugin_data['aiida_version'] = str(parsed.constraint)
            elif pypi_info_data.get('requires_dist') is None:
                missing_pypi_requires = True

            # NOTE cannot read 'entry_points' from PyPI JSON
            # (would have to download wheel and read from there)

    # Now get missing data from the repository
    plugin_info_url = plugin_data.pop('plugin_info', None)
    if plugin_info_url is None:
        REPORTER.warn('Missing plugin_info key!')
    else:
        # retrive content of build file
        plugin_info_content = fetch_file(plugin_info_url)
        # Identify build system
        build_tool_name = identify_build_tool(plugin_info_url,
                                              plugin_info_content)
        if pypi_info:
            data = get_data_parser(build_tool_name)(
                plugin_info_content, ep_only=True)  # , entry_points_only=True
            plugin_data['entry_points'] = data.entry_points
        else:
            data = get_data_parser(build_tool_name)(plugin_info_content,
                                                    ep_only=False)
            plugin_data['metadata'] = data.metadata
            plugin_data['aiida_version'] = data.aiida_version
            plugin_data['entry_points'] = data.entry_points

    # run validations

    if plugin_data['name'] == 'aiida-core' and plugin_data['metadata'].get(
            'version'):
        plugin_data[
            'aiida_version'] = f'=={plugin_data["metadata"]["version"]}'
    if plugin_data.get('aiida_version') is None:
        if not missing_pypi_requires:  # this was likely the issue
            REPORTER.warn('AiiDA version not specified')

    validate_dev_status(plugin_data)

    if 'documentation_url' in plugin_data:
        validate_doc_url(plugin_data['documentation_url'])

    validate_plugin_entry_points(plugin_data)

    return plugin_data


def validate_dev_status(plugin_data: dict):
    """Validate the development_status key, potentially sourcing from classifiers."""
    classifiers = plugin_data['metadata'].get(
        'classifiers', []) if plugin_data.get('metadata', None) else []
    if plugin_data['metadata'] and 'Framework :: AiiDA' not in classifiers:
        REPORTER.warn("Missing classifier 'Framework :: AiiDA'")

    # Read development status from plugin repo
    development_status = None
    for classifier in classifiers:
        if classifier in classifier_to_status:
            if development_status is not None:
                REPORTER.warn(
                    'Multiple development statuses found in classifiers')
            development_status = classifier_to_status[classifier]

    if development_status and 'development_status' in plugin_data and (
            development_status != plugin_data['development_status']):
        REPORTER.warn(
            f'Development status in classifiers ({development_status}) '
            f"does not match development_status in metadata ({plugin_data['development_status']})"
        )

    # prioritise development_status from plugins.json
    if 'development_status' in plugin_data:
        REPORTER.warn(
            '`development_status` key is deprecated. '
            'Use PyPI Trove classifiers in the plugin repository instead.')
    else:
        plugin_data['development_status'] = development_status or 'planning'

    # note: for more validation, it might be sensible to switch to voluptuous
    if plugin_data['development_status'] not in list(status_dict.keys()):
        REPORTER.warn("Invalid development status '{}'".format(
            plugin_data['development_status']))


def validate_doc_url(url):
    """Validate that documentation URL provides valid HTTP response."""
    try:
        response = requests.get(url)
        response.raise_for_status(
        )  # raise an exception for all 4xx/5xx errors
    except Exception:  # pylint: disable=broad-except
        REPORTER.warn('Unable to reach documentation URL: {}'.format(url))
        REPORTER.debug(traceback.print_exc(file=sys.stdout))


def validate_plugin_entry_points(plugin_data):
    """Validate that all entry points registered by the plugin start with the registered entry point root."""
    if plugin_data['name'] == 'aiida-core':
        return

    if 'entry_point_prefix' in plugin_data:
        entry_point_root = plugin_data['entry_point_prefix']
        if not 'aiida_' + plugin_data['entry_point_prefix'].lower(
        ) == plugin_data['package_name'].lower():
            REPORTER.warn(
                f"Prefix \'{plugin_data['entry_point_prefix']}\' does not follow naming convention."
            )
    else:
        # plugin should not specify any entry points
        entry_point_root = 'MISSING'

    for ept_group, ept_list in (plugin_data['entry_points'] or {}).items():
        # we only restrict aiida's entry point groups
        if not ept_group.startswith('aiida.'):
            continue

        for ept_string in ept_list:
            if not isinstance(ept_list, dict):
                ept_string, _path = ept_string.split('=')
                ept_string = ept_string.strip()
            if not ept_string.startswith(entry_point_root):
                REPORTER.warn(
                    f"Entry point '{ept_string}' does not start with prefix '{entry_point_root}.'"
                )


def fetch_metadata(filter_list=None):
    """Fetch metadata from PyPI and AiiDA-Plugins."""
    with open(PLUGINS_FILE_ABS) as handle:
        plugins_raw_data: dict = json.load(handle)

    plugins_metadata = OrderedDict()

    for plugin_name, plugin_data in sorted(plugins_raw_data.items()):
        if filter_list and plugin_name not in filter_list:
            continue
        REPORTER.set_plugin_name(plugin_name)
        plugin_data['name'] = plugin_name
        plugins_metadata[plugin_name] = complete_plugin_data(plugin_data)

    with open(PLUGINS_METADATA, 'w') as handle:
        json.dump(plugins_metadata, handle, indent=2)
    REPORTER.info(f'{PLUGINS_METADATA} dumped')

    if os.environ.get('GITHUB_ACTIONS') == 'true':
        print('::set-output name=error::' + '%0A'.join(REPORTER.warnings))
