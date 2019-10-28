# -*- coding: utf-8 -*-
"""Fetch metadata from plugins and dump it to temporary JSON file.

This fetches metadata from plugins defined using different build systems
 * setuptools/pip: setup.json
 * poetry: pyproject.toml
 * flit: pyproject.toml
"""
from __future__ import absolute_import
from __future__ import print_function
import six
from six.moves import range
import json
import os
import sys
from collections import OrderedDict

import requests
import requests_cache
import tomlkit
from . import PLUGINS_METADATA, PLUGINS_FILE_ABS, state_dict

if os.environ.get('CACHE_REQUESTS'):
    # Set environment variable CACHE_REQUESTS to cache requests for 1 day for faster testing
    # e.g.: export CACHE_REQUESTS=1
    requests_cache.install_cache('demo_cache', expire_after=60 * 60 * 24)


def get_hosted_on(url):
    from six.moves import urllib
    try:
        requests.get(url, timeout=30)
    except Exception:
        raise ValueError("Unable to open 'code_home' url: '{}'".format(url))

    netloc = urllib.parse.urlparse(url).netloc

    # Remove port (if any)
    netloc = netloc.partition(':')[0]

    # Remove subdomains (this only works for domain suffixes of length 1!)
    # TODO: fix it for domains like yyy.co.uk
    netloc = ".".join(netloc.split('.')[-2:])

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
    except Exception:
        import traceback
        print("  >> UNABLE TO RETRIEVE THE PLUGIN INFO URL: {}".format(url))
        print(traceback.print_exc(file=sys.stdout))
        return None

    if 'pyproject.toml' in url:
        try:
            pyproject = tomlkit.parse(response.content)
        except tomlkit.exceptions.TOMLKitError:
            print("  >> WARNING! Unable to parse TOML")

        for buildsystem in ("poetry", "flit"):
            if buildsystem in pyproject["tool"]:
                return (buildsystem, pyproject)
        print("  >> WARNING! Unknown build system in pyproject.toml")
    else:
        try:
            return ("setuptools", json.loads(response.content))
        except ValueError:
            print("  >> WARNING! Unable to parse JSON")

    return None


def get_aiida_version_setup_json(setup_json):
    """Get AiiDA version that this plugin is compatible with.
    """
    import requirements

    try:
        install_requires = setup_json["install_requires"]
        reqs = requirements.parse("\n".join(install_requires))

        aiida_specs = []
        for r in reqs:
            # note: this also catches aiida-core[extra1]
            if r.name in ['aiida-core', 'aiida_core', 'aiida']:
                aiida_specs += r.specs

        if not aiida_specs:
            print("  >> AIIDA VERSION NOT SPECIFIED")
            return None

        # precedence of version specs, from high to low
        precedence = ['==', '>=', '>', '<=', '<']
        sort_order = {precedence[i]: i for i in range(len(precedence))}
        aiida_specs = sorted(aiida_specs,
                             key=lambda r: sort_order.get(r[0], 10))

        # first index: operator (e,g, '>=')
        # second index: version (e.g. '0.12.0rc2')
        # In the future, this can be used to e.g. display a banner for 1.0-compatible plugins
        return ",".join([s[0] + s[1] for s in aiida_specs])

    except KeyError:
        return None


def get_aiida_version_poetry(pyproject):
    """Get AiiDA version that this plugin is compatible with from a pyproject.toml.
    """

    try:
        deps = pyproject["tool"]["poetry"]["dependencies"]
    except KeyError:
        return None

    for name, data in deps.items():
        if name not in ["aiida-core", "aiida_core", "aiida"]:
            continue

        try:  # data is either a dict {"version": ..., "extras": ["..", ], }
            version = data["version"]
        except TypeError:  # or directly the version string
            version = data

        break
    else:
        print("  >> AIIDA VERSION NOT SPECIFIED")
        return None

    from poetry.semver import parse_constraint

    try:
        return str(parse_constraint(version))
    except ValueError:
        print(
            "  >> WARNING: Invalid version encountered in Poetry pyproject.toml for aiida-core"
        )

    return None


def get_plugin_info(plugin_info):
    infos = {
        "entry_points": {},
        "summaryinfo": None,
        "metadata": None,
        "aiida_version": None,
    }

    if plugin_info is None:
        return infos

    buildsystem, data = plugin_info

    if buildsystem not in ["setuptools", "poetry", "flit"]:
        print("  >> WARNING! build system '{}' is not supported".format(
            buildsystem))
        return infos

    try:
        if buildsystem == "setuptools":
            infos["entry_points"].update(
                data["entry_points"])  # updating it gives us a copy
        elif buildsystem == "poetry":
            infos["entry_points"].update({
                group: ["{} = {}".format(k, v) for k, v in entries.items()]
                for group, entries in data["tool"]["poetry"]
                ["plugins"].items()
            })
        elif buildsystem == "flit":
            infos["entry_points"].update({
                group: ["{} = {}".format(k, v) for k, v in entries.items()]
                for group, entries in data["tool"]["flit"]
                ["entrypoints"].items()
            })
    except KeyError:
        pass

    if buildsystem == "setuptools":
        METADATA_KEYS = ["author", "author_email", "version", "description"]
        infos["metadata"] = {
            k: data[k] if k in data else ""
            for k in METADATA_KEYS
        }

        # pylint: disable=unsupported-assignment-operation
        infos["aiida_version"] = get_aiida_version_setup_json(data)
        infos["metadata"]["classifiers"] = data[
            'classifiers'] if 'classifiers' in data else []

        if 'Framework :: AiiDA' not in infos['metadata']["classifiers"]:  # pylint: disable=unsubscriptable-object
            print("  >> WARNING: Missing classifier 'Framework :: AiiDA'")

    elif buildsystem == "poetry":
        # all the following fields are mandatory in Poetry
        infos["metadata"] = {
            "version":
            data["tool"]["poetry"]["version"],
            "description":
            data["tool"]["poetry"]["description"],
            # the authors is a list of the strings of the form "name <email>"
            "author":
            ", ".join(
                a.split("<")[0].strip()
                for a in data["tool"]["poetry"]["authors"]),
        }
        infos["aiida_version"] = get_aiida_version_poetry(data)
    elif buildsystem == "flit":
        # version is not part of the metadata but expected to available in <module>/__init__.py:__version__
        # description is available as a reference in `description-file` (requires another fetch)
        # author is a mandatory field in Flit
        infos["metadata"] = {
            "author": data["tool"]["flit"]["metadata"]["author"],
            "version": "",
            "description": "",
        }
        print("  >> WARNING! version & description metadata and AiiDA version"
              " are not (yet) parsed from the Flit buildsystem pyproject.toml")

    return infos


def format_entry_points_list(ep_list):
    """Return string of entry points, respecting some limit."""
    import copy
    max_len = 5
    tmp = sorted(copy.copy(ep_list))
    if len(tmp) > max_len:
        tmp = tmp[:max_len] + ['...']

    return ", ".join(tmp)


def complete_plugin_data(plugin_data):
    """Update plugin data dictionary used for rendering."""

    # Get link to setup.json file (set to None if not retrievable)
    try:
        plugin_info_link = plugin_data['plugin_info']
    except KeyError:
        print("  >> WARNING: Missing plugin_info!!!")
        plugin_data['plugin_info'] = None
    else:
        plugin_data['plugin_info'] = fetch_plugin_info(plugin_info_link)

    if 'package_name' not in list(plugin_data.keys()):
        plugin_data['package_name'] = plugin_data['name'].replace('-', '_')

    plugin_data['hosted_on'] = get_hosted_on(plugin_data['code_home'])

    plugin_data.update(get_plugin_info(plugin_data['plugin_info']))

    # note: for more validation, it might be sensible to switch to voluptuous
    if plugin_data['state'] not in list(state_dict.keys()):
        print("  >> WARNING: Invalid state {}".format(plugin_data['state']))

    validate_plugin_entry_points(plugin_data)

    return plugin_data


def validate_plugin_entry_points(plugin_data):
    """Validate that all registered entry points start with the registered entry point root."""

    try:
        entry_point_root = plugin_data['entry_point']
    except KeyError:
        # plugin should not specify entry points
        entry_point_root = 'MISSING'

    for ep_list in plugin_data['entry_points'].values():
        for ep in ep_list:
            ep_string, _path = ep.split('=')
            ep_string = ep_string.strip()
            if not ep_string.startswith(entry_point_root):
                print(
                    "  >> WARNING: Entry point '{}' does not start with '{}'".
                    format(ep_string, entry_point_root))


def fetch_metadata():

    with open(PLUGINS_FILE_ABS) as f:
        plugins_raw_data = json.load(f)

    plugins_metadata = OrderedDict()

    for plugin_name, plugin_data in sorted(six.iteritems(plugins_raw_data)):
        print("  - {}".format(plugin_name))

        plugin_data = complete_plugin_data(plugin_data)
        plugins_metadata[plugin_name] = plugin_data

    with open(PLUGINS_METADATA, 'w') as handle:
        json.dump(plugins_metadata, handle, indent=2)
    print("  - {} dumped".format(PLUGINS_METADATA))
