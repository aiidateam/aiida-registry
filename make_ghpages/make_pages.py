#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
import codecs
import json
import os
import shutil
import sys
from six.moves import urllib
from collections import OrderedDict, defaultdict

## Requires jinja2 >= 2.9
from jinja2 import Environment, PackageLoader, select_autoescape
from kitchen.text.converters import getwriter

UTF8Writer = getwriter('utf8')
sys.stdout = UTF8Writer(sys.stdout)

pwd = os.path.split(os.path.abspath(__file__))[0]
apps_file_abs = os.path.join(pwd, os.pardir, 'plugins.json')
templates_folder = 'templates'
out_folder = 'out'
static_folder = 'static'

# Name for subfolder where HTMLs for plugins are going to be sitting
html_subfolder_name = 'apps'

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

## dictionary of human-readable entrypointtypes
entrypointtypes = {k: v['longname'] for k, v in entrypoint_metainfo.items()}


def get_html_plugin_fname(plugin_name):
    import string
    valid_characters = set(string.ascii_letters + string.digits + '_-')

    simple_string = "".join(c for c in plugin_name if c in valid_characters)

    return "{}.html".format(simple_string)


def get_hosted_on(url):
    try:
        urllib.request.urlopen(url, timeout=30)
    except Exception:
        raise ValueError("Unable to open 'code_home' url: '{}'".format(url))

    netloc = urllib.parse.urlparse(url).netloc

    # Remove port (if any)
    netloc = netloc.partition(':')[0]

    # Remove subdomains (this only works for domain suffixes of length 1!)
    # TODO: fix it for domains like yyy.co.uk
    netloc = ".".join(netloc.split('.')[-2:])

    return netloc


def get_setup_info(json_url):
    try:
        response = urllib.request.urlopen(json_url)
        json_txt = response.read()
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


if __name__ == "__main__":  # noqa: MC0001
    outdir_abs = os.path.join(pwd, out_folder)
    static_abs = os.path.join(pwd, static_folder)

    # Create output folder, copy static files
    if os.path.exists(outdir_abs):
        shutil.rmtree(outdir_abs)
    os.mkdir(outdir_abs)
    shutil.copytree(static_abs, os.path.join(outdir_abs, static_folder))

    env = Environment(
        loader=PackageLoader('mod'),
        autoescape=select_autoescape(['html', 'xml']),
    )

    singlepage_template = env.get_template("singlepage.html")
    main_index_template = env.get_template("main_index.html")

    with open(apps_file_abs) as f:
        plugins_raw_data = json.load(f)

    all_data = {}
    all_data['plugins'] = OrderedDict()

    html_subfolder_abs = os.path.join(outdir_abs, html_subfolder_name)
    os.mkdir(html_subfolder_abs)

    summaries = defaultdict(list)
    #    calculations_summary = []
    #    parsers_summary = []
    #    data_summary = []
    #    workflows_summary = []
    other_summary = []
    other_summary_names = set()

    for plugin_name in sorted(plugins_raw_data.keys()):
        print("  - {}".format(plugin_name))
        plugin_data = plugins_raw_data[plugin_name]

        thisplugin_data = {}

        html_plugin_fname = get_html_plugin_fname(plugin_name)
        subpage_name = os.path.join(html_subfolder_name,
                                    get_html_plugin_fname(plugin_name))
        subpage_abspath = os.path.join(outdir_abs, subpage_name)
        hosted_on = get_hosted_on(plugin_data['code_home'])

        # Get now the setup.json from the project; should be set to None
        # if not retrievable
        setupinfo = None
        try:
            the_plugin_info = plugin_data['plugin_info']
        except KeyError:
            print("  >> WARNING: Missing plugin_info!!!")
            setupinfo = None
        else:
            setupinfo = get_setup_info(the_plugin_info)
        plugin_data['setupinfo'] = setupinfo
        plugin_data['subpage'] = subpage_name
        plugin_data['hosted_on'] = hosted_on
        if plugin_data['setupinfo']:
            plugin_data['setupinfo']['package_name'] = plugin_data[
                'setupinfo']['name'].replace('-', '_')

        ## add a static entrypointtypes dictionary
        plugin_data['entrypointtypes'] = entrypointtypes

        ## Summary info section
        plugin_data['summaryinfo'] = ""
        summary_info_pieces = []
        if setupinfo:
            if 'entry_points' in setupinfo:
                ep = setupinfo['entry_points'].copy()

                for entrypoint_name in main_entrypoints:
                    try:
                        num = len(ep.pop(entrypoint_name))
                        if num > 0:
                            summary_info_pieces.append({
                                "colorclass":
                                entrypoint_metainfo[entrypoint_name]
                                ['colorclass'],
                                "text":
                                entrypoint_metainfo[entrypoint_name]
                                ['shortname'],
                                "count":
                                num
                            })
                            summaries[entrypoint_name].append(num)
                    except KeyError:
                        #No specific entrypoints, pass
                        pass

                # Check remaining non-empty entrypoints
                remaining = [ep_name for ep_name in ep if ep[ep_name]]
                remaining_count = [
                    len(ep[ep_name]) for ep_name in ep if ep[ep_name]
                ]
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
                                ep_name.replace('_',
                                                ' ').replace('.',
                                                             ' ').capitalize())

                    summary_info_pieces.append({
                        "colorclass":
                        othercolorclass,
                        "text":
                        'Other ({})'.format(", ".join(other_elements)),
                        "count":
                        total_count
                    })
                    other_summary.append(total_count)
                    other_summary_names.update(other_elements)

        plugin_data['summaryinfo'] = summary_info_pieces

        all_data['plugins'][plugin_name] = plugin_data

        plugin_html = singlepage_template.render(**plugin_data)

        with codecs.open(subpage_abspath, 'w', 'utf-8') as f:
            f.write(plugin_html)
        print("    - Page {} generated.".format(subpage_name))

    global_summary = []
    for entrypoint_name in main_entrypoints:
        global_summary.append({
            'name':
            entrypoint_metainfo[entrypoint_name]['shortname'],
            'colorclass':
            entrypoint_metainfo[entrypoint_name]['colorclass'],
            'num_entries':
            len(summaries[entrypoint_name]),
            'total_num':
            sum(summaries[entrypoint_name]),
        })

    global_summary.append({
        'name': "Other",
        'tooltip': ", ".join(sorted(other_summary_names)),
        'colorclass': othercolorclass,
        'num_entries': len(other_summary),
        'total_num': sum(other_summary)
    })

    all_data['globalsummary'] = global_summary

    print("[main index]")
    # print all_data
    rendered = main_index_template.render(**all_data)
    outfile = os.path.join(outdir_abs, 'index.html')
    with codecs.open(outfile, 'w', 'utf-8') as f:
        f.write(rendered)
    print("  - index.html generated")
