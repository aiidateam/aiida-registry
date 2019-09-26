#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
import six
from six.moves import range
import codecs
import json
import os
import shutil
import sys
from collections import OrderedDict, defaultdict

## Requires jinja2 >= 2.9
from jinja2 import Environment, PackageLoader, select_autoescape
from kitchen.text.converters import getwriter
import requests
import requests_cache

if os.environ.get('CACHE_REQUESTS'):
    # Set environment variable CACHE_REQUESTS to cache requests for 1 day for faster testing
    # e.g.: export CACHE_REQUESTS=1
    requests_cache.install_cache('demo_cache', expire_after=60 * 60 * 24)

UTF8Writer = getwriter('utf8')
sys.stdout = UTF8Writer(sys.stdout)

# Subfolders
OUT_FOLDER = 'out'
STATIC_FOLDER = 'static'
HTML_FOLDER = 'plugins'  # Name for subfolder where HTMLs for plugins are going to be sitting
TEMPLATES_FOLDER = 'templates'
DATA_JSON = 'all_data.json'

# Absolute paths
pwd = os.path.split(os.path.abspath(__file__))[0]
OUT_FOLDER_ABS = os.path.join(pwd, OUT_FOLDER)
STATIC_FOLDER_ABS = os.path.join(pwd, STATIC_FOLDER)
HTML_FOLDER_ABS = os.path.join(OUT_FOLDER_ABS, HTML_FOLDER)
PLUGINS_FILE_ABS = os.path.join(pwd, os.pardir, 'plugins.json')

# These are the main entrypoints, the other will fall under 'other'
main_entrypoints = [
    'aiida.calculations', 'aiida.parsers', 'aiida.data', 'aiida.workflows'
]
# Color class of the 'other' category
othercolorclass = 'orange'

entrypoint_metainfo = {
    'aiida.calculations': {
        'shortname': "Calculations",
        'longname': "Calculation plugins",
        'colorclass': 'blue'
    },
    'aiida.parsers': {
        'shortname': "Parsers",
        'longname': "Calculation parsers",
        'colorclass': 'brown',
    },
    'aiida.data': {
        'shortname': "Data",
        'longname': "Data types",
        'colorclass': 'red',
    },
    'aiida.workflows': {
        'shortname': "Workflows",
        'longname': "Workflows and WorkChains",
        'colorclass': 'green'
    },
    'aiida.tests': {
        'shortname': "Tests",
        'longname': "Development test modules",
        'colorclass': othercolorclass,
    },
    'console_scripts': {
        'shortname': "Console scripts",
        'longname': "Command-line script utilities",
        'colorclass': othercolorclass,
    },
    'aiida.tools.dbexporters.tcod_plugins': {
        'shortname': "TCOD plugins",
        'longname': "Exporter plugins for the TCOD database",
        'colorclass': othercolorclass
    },
}

# User-facing description of plugin development states
state_dict = {
    'registered': "Not yet ready to use. Developers welcome!",
    'development':
    "Adds new functionality, not yet ready for production. Testing welcome!",
    'stable': "Ready for production calculations. Bug reports welcome!",
}

## dictionary of human-readable entrypointtypes
entrypointtypes = {k: v['longname'] for k, v in entrypoint_metainfo.items()}


def get_html_plugin_fname(plugin_name):
    import string
    valid_characters = set(string.ascii_letters + string.digits + '_-')

    simple_string = "".join(c for c in plugin_name if c in valid_characters)

    return "{}.html".format(simple_string)


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


def get_setup_json(json_url):
    try:
        response = requests.get(json_url)
        json_txt = response.content
    except Exception:
        import traceback
        print("  >> UNABLE TO RETRIEVE THE JSON URL: {}".format(json_url))
        print(traceback.print_exc(file=sys.stdout))
        return None
    try:
        json_data = json.loads(json_txt)
    except ValueError:
        print("  >> WARNING! Unable to parse JSON")
        return None

    return json_data


def get_aiida_version(setup_json):
    """Get AiiDA version that this plugin is compatible with.
    """
    import requirements

    if setup_json is None:
        return None

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


def get_summary_info(setup_json):
    """Get info for plugin detail page.
    """
    summary_info = []

    if setup_json is None:
        return summary_info

    if 'entry_points' in setup_json:
        ep = setup_json['entry_points'].copy()

        for entrypoint_name in main_entrypoints:
            try:
                num = len(ep.pop(entrypoint_name))
                if num > 0:
                    summary_info.append({
                        "colorclass":
                        entrypoint_metainfo[entrypoint_name]['colorclass'],
                        "text":
                        entrypoint_metainfo[entrypoint_name]['shortname'],
                        "count":
                        num
                    })
                    entrypoints_count[entrypoint_name].append(num)
            except KeyError:
                #No specific entrypoints, pass
                pass

        # Check remaining non-empty entrypoints
        remaining = [ep_name for ep_name in ep if ep[ep_name]]
        remaining_count = [len(ep[ep_name]) for ep_name in ep if ep[ep_name]]
        total_count = sum(remaining_count)
        if total_count:
            other_elements = []
            for ep_name in remaining:
                try:
                    other_elements.append(
                        entrypoint_metainfo[ep_name]['shortname'])
                except KeyError:
                    for strip_prefix in ['aiida.']:
                        if ep_name.startswith(strip_prefix):
                            ep_name = ep_name[len(strip_prefix):]
                            break
                    other_elements.append(
                        ep_name.replace('_', ' ').replace('.',
                                                          ' ').capitalize())

            summary_info.append({
                "colorclass":
                othercolorclass,
                "text":
                'Other ({})'.format(format_entry_points_list(other_elements)),
                "count":
                total_count
            })
            entrypoints_count['other'].append(total_count)
            other_entrypoint_names.update(other_elements)

    return summary_info


def format_entry_points_list(ep_list):
    """Return string of entry points, respecting some limit."""
    import copy
    max_len = 5
    tmp = sorted(copy.copy(ep_list))
    if len(tmp) > max_len:
        tmp = tmp[:max_len] + ['...']

    return ", ".join(tmp)


def complete_plugin_data(plugin_data, subpage_name):
    """Update plugin data dictionary used for rendering."""

    # Get link to setup.json file (set to None if not retrievable)
    try:
        setup_json_link = plugin_data['plugin_info']
    except KeyError:
        print("  >> WARNING: Missing plugin_info!!!")
        plugin_data['setup_json'] = None
    else:
        plugin_data['setup_json'] = get_setup_json(setup_json_link)

        if 'package_name' not in list(plugin_data.keys()):
            plugin_data['package_name'] = plugin_data['name'].replace('-', '_')

    plugin_data['subpage'] = subpage_name
    plugin_data['hosted_on'] = get_hosted_on(plugin_data['code_home'])
    plugin_data[
        'entrypointtypes'] = entrypointtypes  # add a static entrypointtypes dictionary
    plugin_data['summaryinfo'] = get_summary_info(plugin_data['setup_json'])
    plugin_data['aiida_version'] = get_aiida_version(plugin_data['setup_json'])

    plugin_data['state_dict'] = state_dict
    # note: for more validation, it might be sensible to switch to voluptuous
    if plugin_data['state'] not in list(state_dict.keys()):
        print("  >> WARNING: Invalid state {}".format(plugin_data['state']))

    return plugin_data


def global_summary():
    """Compute summary of plugin registry."""
    global_summary = []
    for entrypoint_name in main_entrypoints:
        global_summary.append({
            'name':
            entrypoint_metainfo[entrypoint_name]['shortname'],
            'colorclass':
            entrypoint_metainfo[entrypoint_name]['colorclass'],
            'num_entries':
            len(entrypoints_count[entrypoint_name]),
            'total_num':
            sum(entrypoints_count[entrypoint_name]),
        })

    global_summary.append({
        'name':
        "Other",
        'tooltip':
        format_entry_points_list(other_entrypoint_names),
        'colorclass':
        othercolorclass,
        'num_entries':
        len(entrypoints_count['other']),
        'total_num':
        sum(entrypoints_count['other'])
    })

    return global_summary


if __name__ == "__main__":

    # Create output folder, copy static files
    if os.path.exists(OUT_FOLDER_ABS):
        shutil.rmtree(OUT_FOLDER_ABS)
    os.mkdir(OUT_FOLDER_ABS)
    os.mkdir(HTML_FOLDER_ABS)
    shutil.copytree(STATIC_FOLDER_ABS,
                    os.path.join(OUT_FOLDER_ABS, STATIC_FOLDER))

    env = Environment(
        loader=PackageLoader('mod'),
        autoescape=select_autoescape(['html', 'xml']),
    )

    with open(PLUGINS_FILE_ABS) as f:
        plugins_raw_data = json.load(f)

    # Note: These are *global* variables
    all_data = {}
    all_data['plugins'] = OrderedDict()
    entrypoints_count = defaultdict(list)
    other_entrypoint_names = set()

    # Create HTML view for each plugin
    for plugin_name, plugin_data in sorted(six.iteritems(plugins_raw_data)):
        print("  - {}".format(plugin_name))

        subpage_name = os.path.join(HTML_FOLDER,
                                    get_html_plugin_fname(plugin_name))
        subpage_abspath = os.path.join(OUT_FOLDER_ABS, subpage_name)
        plugin_data = complete_plugin_data(plugin_data, subpage_name)

        # Write plugin html
        plugin_html = env.get_template("singlepage.html").render(**plugin_data)
        with codecs.open(subpage_abspath, 'w', 'utf-8') as f:
            f.write(plugin_html)
        print("    - Page {} generated.".format(subpage_name))

        all_data['plugins'][plugin_name] = plugin_data

    all_data['globalsummary'] = global_summary()

    print("[main index]")
    rendered = env.get_template("main_index.html").render(**all_data)
    outfile = os.path.join(OUT_FOLDER_ABS, 'index.html')
    with codecs.open(outfile, 'w', 'utf-8') as f:
        f.write(rendered)
    print("  - index.html generated")

    with open(DATA_JSON, 'w') as handle:
        json.dump(all_data, handle, indent=2)
    print("  - {} dumped".format(DATA_JSON))
