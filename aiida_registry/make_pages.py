# -*- coding: utf-8 -*-
"""Generate HTML pages for plugin registry.

Reads plugin-metadata.json produced by fetch_metadata.
"""
# pylint: disable=missing-function-docstring,invalid-name,global-statement

import codecs
import json
import os
import copy
import shutil
import string
from collections import defaultdict
from jinja2 import Environment, PackageLoader, select_autoescape

from . import OTHERCOLORCLASS, entrypoint_metainfo, main_entrypoints, PLUGINS_METADATA, entrypointtypes, status_dict

# Subfolders
OUT_FOLDER = 'out'
STATIC_FOLDER = 'static'
HTML_FOLDER = 'plugins'  # Name for subfolder where HTMLs for plugins are going to be sitting
TEMPLATES_FOLDER = 'templates'

# Absolute paths
pwd = os.path.split(os.path.abspath(__file__))[0]
STATIC_FOLDER_ABS = os.path.join(pwd, STATIC_FOLDER)

entrypoints_count = defaultdict(list)
other_entrypoint_names = set()


def get_html_plugin_fname(plugin_name):
    valid_characters = set(string.ascii_letters + string.digits + '_-')

    simple_string = ''.join(c for c in plugin_name if c in valid_characters)

    return '{}.html'.format(simple_string)


def get_summary_info(entry_points):
    """Get info for plugin detail page.
    """
    global entrypoints_count, other_entrypoint_names

    summary_info = []
    ep = entry_points.copy()

    # Collect "main" entry points first
    for entrypoint_name in main_entrypoints:
        try:
            num = len(ep.pop(entrypoint_name))
            if num > 0:
                summary_info.append({
                    'colorclass':
                    entrypoint_metainfo[entrypoint_name]['colorclass'],
                    'text':
                    entrypoint_metainfo[entrypoint_name]['shortname'],
                    'count':
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
                    ep_name.replace('_', ' ').replace('.', ' ').capitalize())

        summary_info.append({
            'colorclass':
            OTHERCOLORCLASS,
            'text':
            'Other ({})'.format(format_entry_points_list(other_elements)),
            'count':
            total_count
        })
        entrypoints_count['other'].append(total_count)
        other_entrypoint_names.update(other_elements)

    return summary_info


def format_entry_points_list(ep_list):
    """Return string of entry points, respecting some limit."""
    max_len = 3
    tmp = sorted(copy.copy(ep_list))
    if len(tmp) > max_len:
        tmp = tmp[:max_len] + ['...']

    return ', '.join(tmp)


def global_summary():
    """Compute summary of plugin registry."""
    global entrypoints_count, other_entrypoint_names

    summary = []
    for entrypoint_name in main_entrypoints:
        summary.append({
            'name':
            entrypoint_metainfo[entrypoint_name]['shortname'],
            'colorclass':
            entrypoint_metainfo[entrypoint_name]['colorclass'],
            'num_entries':
            len(entrypoints_count[entrypoint_name]),
            'total_num':
            sum(entrypoints_count[entrypoint_name]),
        })

    summary.append({
        'name': 'Other',
        'tooltip': format_entry_points_list(other_entrypoint_names),
        'colorclass': OTHERCOLORCLASS,
        'num_entries': len(entrypoints_count['other']),
        'total_num': sum(entrypoints_count['other'])
    })

    return summary


def get_pip_install_cmd(plugin_data):

    pip_url = plugin_data['pip_url']
    if pip_url.startswith('http') or pip_url.startswith('git'):
        return 'pip install {}'.format(pip_url)

    # else, we assume it's a PyPI package and we would like to add the version
    try:
        version = plugin_data['metadata']['version']
        pre_releases = ['a', 'b', 'rc']
        if any([version.find(p_id) != -1 for p_id in pre_releases]):
            return 'pip install --pre {}'.format(pip_url)
        return 'pip install {}'.format(pip_url)
    except KeyError:
        return 'pip install {}'.format(pip_url)


def make_pages():

    # Create output folder, copy static files
    if os.path.exists(OUT_FOLDER):
        shutil.rmtree(OUT_FOLDER)
    os.mkdir(OUT_FOLDER)
    os.mkdir(os.path.join(OUT_FOLDER, HTML_FOLDER))
    shutil.copytree(STATIC_FOLDER_ABS, os.path.join(OUT_FOLDER, STATIC_FOLDER))

    env = Environment(
        loader=PackageLoader('aiida_registry.mod'),
        autoescape=select_autoescape(['html', 'xml']),
    )

    with open(PLUGINS_METADATA) as f:
        plugins_metadata = json.load(f)

    # Create HTML view for each plugin
    for plugin_name, plugin_data in plugins_metadata.items():
        print('  - {}'.format(plugin_name))

        subpage = os.path.join(HTML_FOLDER, get_html_plugin_fname(plugin_name))
        subpage_abspath = os.path.join(OUT_FOLDER, subpage)

        plugin_data['subpage'] = subpage
        plugin_data[
            'entrypointtypes'] = entrypointtypes  # add a static entrypointtypes dictionary

        plugin_data['summaryinfo'] = get_summary_info(
            plugin_data['entry_points'])
        plugin_data['status_dict'] = status_dict
        plugin_data['pip_install_cmd'] = get_pip_install_cmd(plugin_data)

        # Write plugin html
        plugin_html = env.get_template('singlepage.html').render(**plugin_data)
        with codecs.open(subpage_abspath, 'w', 'utf-8') as f:
            f.write(plugin_html)
        print('    - Page {} generated.'.format(subpage))

    all_data = {}
    all_data['plugins'] = plugins_metadata
    all_data['globalsummary'] = global_summary()

    print('[main index]')
    rendered = env.get_template('main_index.html').render(**all_data)
    outfile = os.path.join(OUT_FOLDER, 'index.html')
    with codecs.open(outfile, 'w', 'utf-8') as f:
        f.write(rendered)
    print('  - index.html generated')
