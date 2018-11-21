#!/usr/bin/env python
# -*- coding: utf-8 -*-
import codecs
import json
import os
import re
import shutil
import sys
from urlparse import urlparse
from collections import OrderedDict, defaultdict

## Requires jinja2 >= 2.9
import jinja2
from jinja2 import Environment, PackageLoader, select_autoescape
from kitchen.text.converters import getwriter
# see https://pythonhosted.org/kitchen/unicode-frustrations.html
from kitchen.text.converters import to_bytes

UTF8Writer = getwriter('utf8')
sys.stdout = UTF8Writer(sys.stdout)

pwd = os.path.split(os.path.abspath(__file__))[0]
plugins_file_abs = os.path.join(pwd, os.pardir, 'plugins.json')
templates_folder = 'templates'
out_folder = 'out'
static_folder = 'static'

# Name for subfolder where HTMLs for plugins are going to be sitting
html_subfolder_name = 'plugins'

# These are the main entrypoints, the other will fall under 'other'
main_entrypoints = ['aiida.calculations', 'aiida.parsers', 'aiida.data', 'aiida.workflows']
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
        'longname':  "Exporter plugins for the TCOD database",
        'colorclass': othercolorclass
    },
}

## dictionary of human-readable entrypointtypes
entrypointtypes = {k: v['longname'] for k, v in entrypoint_metainfo.items()}

# def escape_except_newline(string):
#     """
#     Custom jinja2 filter to escape a string, and afterwards replace newlines
#     with
#     (unescaped) <br> tags.
#     """
#     import jinja2
#     string = unicode(jinja2.escape(string))
#     return jinja2.Markup(string.replace(u'\n', u'<br/>\n'))


# def escape_except_whitelist(string):
#     """
#     Custom jinja2 filter to escape a string, except some whitelist of tags

#     Note: only tags without attributes are supported

#     TODO: make it MUCH more robust than this...
#     """
#     import jinja2

#     # Whitelisted tags
#     whitelist = ['sub', 'sup']

#     # Each element is a tuple with a string and a boolean;
#     # the second says True if it is a string to further consider, split and then
#     # eventually escape, or False if it only contains
#     string_pieces = [(string, True)]

#     for tagname in whitelist:
#         for tag in ["<{}>".format(tagname), "</{}>".format(tagname)]:
#             new_pieces = []
#             for string_piece, to_process in string_pieces:
#                 if not to_process:
#                     new_pieces.append((string_piece, to_process))
#                 else:
#                     pieces = string_piece.split(tag)
#                     if pieces:
#                         new_pieces.append((pieces[0], True))
#                         for piece in pieces[1:]:
#                             new_pieces.append((tag, False))
#                             new_pieces.append((piece, True))
#             string_pieces = new_pieces

#     final_pieces = []
#     for piece in string_pieces:
#         if piece[1]:
#             final_pieces.append(unicode(jinja2.escape(piece[0])))
#         else:
#             final_pieces.append(unicode(piece[0]))

#     return jinja2.Markup("".join(final_pieces))

def get_html_plugin_fname(plugin_name):
    import string
    valid_characters = set(string.ascii_letters + string.digits + '_-')

    simple_string = "".join(c for c in plugin_name if c in valid_characters)

    return "{}.html".format(simple_string)

def get_hosted_on(url):
    try:
        netloc = urlparse(plugin_data['code_home']).netloc
    except Exception as e:
    	print e
        return None

    # Remove port (if any)
    netloc = netloc.partition(':')[0]

    # Remove subdomains (this only works for domain suffixes of length 1!)
    # TODO: fix it for domains like yyy.co.uk
    netloc = ".".join(netloc.split('.')[-2:])

    return netloc

def get_setup_info(json_url):
	import urllib2
	try:
		response = urllib2.urlopen(json_url)
		json_txt = response.read()
	except Exception as e:
		import traceback
		print "  >> UNABLE TO RETRIEVE THE JSON URL: {}".format(json_url)
		print traceback.print_exc(file=sys.stdout)
		return None
	try:
		json_data = json.loads(json_txt)
	except ValueError:
		print "  >> WARNING! Unable to parse JSON"
		return None

	return json_data

if __name__ == "__main__":
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
    #env.filters['escape_except_newline'] = escape_except_newline
    #env.filters['escape_except_whitelist'] = escape_except_whitelist

    singlepage_template = env.get_template("singlepage.html")
    main_index_template = env.get_template("main_index.html")


    with open(plugins_file_abs) as f:
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
        print "  - {}".format(plugin_name)
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
        	print "  >> WARNING: Missing plugin_info!!!"
        	setupinfo = None
        else:
	        setupinfo = get_setup_info(the_plugin_info)
        plugin_data['setupinfo'] = setupinfo
        plugin_data['subpage'] = subpage_name
        plugin_data['hosted_on'] = hosted_on
        if plugin_data['setupinfo']:
            plugin_data['setupinfo']['package_name'] = plugin_data['setupinfo']['name'].replace('-', '_')

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
                                "colorclass": entrypoint_metainfo[entrypoint_name]['colorclass'],
                                "text": entrypoint_metainfo[entrypoint_name]['shortname'],
                                "count": num
                                })
                            summaries[entrypoint_name].append(num)
                    except KeyError:
                        #No specific entrypoints, pass
                        pass


                # try:
                #     num = len(ep.pop('aiida.calculations'))
                #     if num > 0:
                #         summary_info_pieces.append({
                #             "colorclass": "blue",
                #             "text": "Calculations",
                #             "count": num
                #             })
                #         calculations_summary.append(num)
                # except KeyError:
                #     #No specific entrypoints, pass
                #     pass
                # try:
                #     num = len(ep.pop('aiida.parsers'))
                #     if num > 0:
                #         summary_info_pieces.append({
                #             "colorclass": "brown",
                #             "text": "Parsers",
                #             "count": num
                #             })
                #     parsers_summary.append(num)
                # except KeyError:
                #     #No specific entrypoints, pass
                #     pass
                
                # try:
                #     num = len(ep.pop('aiida.data'))
                #     if num > 0:
                #         summary_info_pieces.append({
                #             "colorclass": "red",
                #             "text": "Data",
                #             "count": num
                #             })
                #         data_summary.append(num)
                # except KeyError:
                #     #No specific entrypoints, pass
                #     pass

                # try:
                #     num = len(ep.pop('aiida.workflows'))
                #     if num > 0:
                #         summary_info_pieces.append({
                #             "colorclass": "green",
                #             "text": "Workflows",
                #             "count": num
                #             })
                #         workflows_summary.append(num)
                # except KeyError:
                #     #No specific entrypoints, pass
                #     pass
                
                # Check remaining non-empty entrypoints
                remaining = [ep_name for ep_name in ep if len(ep[ep_name]) > 0 ]
                remaining_count = [len(ep[ep_name]) for ep_name in ep if len(ep[ep_name]) > 0 ]
                total_count = sum(remaining_count)
                if total_count:
                    other_elements = []
                    for ep_name in remaining:
                        try:
                            other_elements.append(entrypoint_metainfo[ep_name]['shortname'])
                        except KeyError:
                            for strip_prefix in ['aiida.']:
                                if ep_name.startswith(strip_prefix):
                                    ep_name = ep_name[len(strip_prefix):]
                                    break
                            other_elements.append(ep_name.replace('_', ' ').replace('.', ' ').capitalize())

                    summary_info_pieces.append({
                        "colorclass": othercolorclass,
                        "text": 'Other ({})'.format(
                            ", ".join(
                                other_elements
                            )),
                        "count": total_count
                        })
                    other_summary.append(total_count)
                    other_summary_names.update(other_elements)

        plugin_data['summaryinfo'] = summary_info_pieces

        all_data['plugins'][plugin_name] = plugin_data

        plugin_html = singlepage_template.render(**plugin_data)

        with codecs.open(subpage_abspath, 'w', 'utf-8') as f:
            f.write(plugin_html)
        print "    - Page {} generated.".format(subpage_name)

    global_summary = []
    for entrypoint_name in main_entrypoints:
        global_summary.append(
            {
                'name': entrypoint_metainfo[entrypoint_name]['shortname'],
                'colorclass': entrypoint_metainfo[entrypoint_name]['colorclass'],
                'num_entries': len(summaries[entrypoint_name]),
                'total_num': sum(summaries[entrypoint_name]),
            })

    # {
    #     'name': "Calculations",
    #     'colorclass': 'blue',
    #     'num_entries': len(calculations_summary),
    #     'total_num': sum(calculations_summary)
    # },
    # {
    #     'name': "Parsers",
    #     'colorclass': 'brown',
    #     'num_entries': len(parsers_summary),
    #     'total_num': sum(parsers_summary)
    # },
    # {
    #     'name': "Data",
    #     'colorclass': 'red',
    #     'num_entries': len(data_summary),
    #     'total_num': sum(data_summary)
    # },
    # {
    #     'name': "Workflows",
    #     'colorclass': 'green',
    #     'num_entries': len(workflows_summary),
    #     'total_num': sum(workflows_summary)
    # }, 
    global_summary.append(       
        {
            'name': "Other",
            'tooltip': ", ".join(sorted(other_summary_names)),
            'colorclass': othercolorclass,
            'num_entries': len(other_summary),
            'total_num': sum(other_summary)
        })      

    all_data['globalsummary'] = global_summary

    print "[main index]"
    # print all_data
    rendered = main_index_template.render(**all_data)
    outfile = os.path.join(outdir_abs, 'index.html')
    with codecs.open(outfile, 'w', 'utf-8') as f:
        f.write(rendered)
    print "  - index.html generated"
