#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Configuration of plugin registry.

 * paths to files & folders
 * info on entry points
 * info on development status
"""

from __future__ import absolute_import
from __future__ import print_function
import os

# Absolute paths
pwd = os.path.split(os.path.abspath(__file__))[0]
PLUGINS_FILE_ABS = os.path.join(pwd, os.pardir, 'plugins.json')
PLUGINS_METADATA = 'plugins_metadata.json'

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