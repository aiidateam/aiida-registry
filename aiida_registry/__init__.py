#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Configuration of plugin registry.

 * paths to files & folders
 * info on entry points
 * info on development status
"""

import os

# Absolute paths
pwd = os.path.split(os.path.abspath(__file__))[0]
PLUGINS_FILE_ABS = os.path.join(pwd, os.pardir, 'plugins.json')
PLUGINS_METADATA = 'plugins_metadata.json'
PLUGINS_METADATA_KEYS = ['author', 'author_email', 'version', 'description']

# These are the main entrypoints, the other will fall under 'other'
main_entrypoints = [
    'aiida.calculations', 'aiida.parsers', 'aiida.data', 'aiida.workflows',
    'console_scripts'
]
# Color class of the 'other' category
OTHERCOLORCLASS = 'orange'

entrypoint_metainfo = {
    'aiida.calculations': {
        'shortname': 'Calculations',
        'longname': 'CalcJobs and calculation functions',
        'colorclass': 'blue'
    },
    'aiida.parsers': {
        'shortname': 'Parsers',
        'longname': 'CalcJob parsers',
        'colorclass': 'brown',
    },
    'aiida.data': {
        'shortname': 'Data',
        'longname': 'Data node types',
        'colorclass': 'red',
    },
    'aiida.cmdline.data': {
        'shortname': 'Data commands',
        'longname': 'verdi data commands',
        'colorclass': OTHERCOLORCLASS,
    },
    'aiida.groups': {
        'shortname': 'Groups',
        'longname': 'Group types',
        'colorclass': OTHERCOLORCLASS,
    },
    'aiida.workflows': {
        'shortname': 'Workflows',
        'longname': 'WorkChains and work functions',
        'colorclass': 'green'
    },
    'aiida.schedulers': {
        'shortname': 'Schedulers',
        'longname': 'Job scheduler support',
        'colorclass': OTHERCOLORCLASS,
    },
    'aiida.transports': {
        'shortname': 'Transports',
        'longname': 'Data transport protocols',
        'colorclass': OTHERCOLORCLASS,
    },
    'aiida.tests': {
        'shortname': 'Tests',
        'longname': 'Development test modules',
        'colorclass': OTHERCOLORCLASS,
    },
    'aiida.tools.dbexporters': {
        'shortname': 'Database Exporters',
        'longname': 'Support for exporting to external databases',
        'colorclass': OTHERCOLORCLASS
    },
    'aiida.tools.dbimporters': {
        'shortname': 'Database Importers',
        'longname': 'Support for importing from external databases',
        'colorclass': OTHERCOLORCLASS
    },
    'console_scripts': {
        'shortname': 'Console scripts',
        'longname': 'Console scripts',
        'colorclass': 'purple',
    },
}

# User-facing description of plugin development status
status_dict = {
    'planning': [
        'Not yet ready to use. Developers welcome!',
        'status-planning-d9644d.svg'
    ],
    'beta': [
        'Adds new functionality, not yet ready for production. Testing welcome!',
        'status-beta-d6af23.svg'
    ],
    'stable': [
        'Ready for production calculations. Bug reports welcome!',
        'status-stable-4cc61e.svg'
    ]
}

## dictionary of human-readable entrypointtypes
entrypointtypes = {k: v['longname'] for k, v in entrypoint_metainfo.items()}
