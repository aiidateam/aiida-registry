# -*- coding: utf-8 -*-
"""Test installing all registered plugins."""
# pylint: disable=missing-function-docstring

import json
import subprocess
import sys

from . import PLUGINS_METADATA


def try_cmd(cmd):
    try:
        return subprocess.check_output(cmd,
                                       shell=True,
                                       stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as exc:
        print(exc.output)
        return False


def has_python_version_classifier(plugin_info):
    """Return True, if package specifies python version compatibility."""
    meta = plugin_info['metadata']

    if meta is None or 'classifiers' not in meta:
        return False

    for classifier in meta['classifiers']:
        if classifier.startswith('Programming Language :: Python ::'):
            return True

    return False


def supports_python_version(plugin_info):
    """Return True, if package supports current python version."""

    # If developers don't specify version compatibility, we assume all versions are supported
    if not has_python_version_classifier(plugin_info):
        return True

    python_version = sys.version_info
    classifier = 'Programming Language :: Python :: {}.{}'.format(
        python_version[0], python_version[1])

    if classifier in plugin_info['metadata']['classifiers']:
        return True

    print('   >> SKIPPING - python version {}.{} not supported'.format(
        python_version[0], python_version[1]))
    return False


def test_install():
    with open(PLUGINS_METADATA, 'r') as handle:
        data = json.load(handle)

    print('[test installing plugins]')
    for _k, val in data.items():

        print(' - {}'.format(val['name']))

        if not supports_python_version(val):
            continue

        # 'planning' plugins aren't installed/tested
        if val['development_status'] == 'planning':
            continue

        if 'pip_url' not in list(val.keys()):
            print('    >> WARNING: Missing pip_url key!')
            continue

        # Idea: create conda environment for each package to isolate installs...
        # print("   - Creating environment for {}".format(val['name']))
        # py_version = "{}.{}".format(sys.version_info[0], sys.version_info[1])
        # is_env_installed = try_cmd("conda create -n {} python={} -y && conda activate"\
        #       .format(val['name'], py_version))
        # if not is_env_installed:
        #     continue

        print('   - Installing {}'.format(val['name']))
        is_package_installed = try_cmd('pip install --pre {}'.format(
            val['pip_url']))

        if not is_package_installed:
            continue

        if 'package_name' not in list(val.keys()):
            val['package_name'] = val['name'].replace('-', '_')

        print('   - Importing {}'.format(val['package_name']))
        try_cmd("python -c 'import {}'".format(val['package_name']))

        # print("   - Removing environment for {}".format(val['name']))
        # is_env_removed = try_cmd("conda env remove -n {}".format(val['name']))
