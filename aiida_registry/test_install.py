# -*- coding: utf-8 -*-
"""Test installing all registered plugins."""
from __future__ import absolute_import
from __future__ import print_function

import json
import six
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
        if classifier.startswith("Programming Language :: Python ::"):
            return True

    return False


def supports_python_version(plugin_info):
    """Return True, if package supports current python version."""

    # If developers don't specify version compatibility, we assume all versions are supported
    if not has_python_version_classifier(plugin_info):
        return True

    python_version = sys.version_info
    classifier = "Programming Language :: Python :: {}.{}".format(
        python_version[0], python_version[1])

    if classifier in plugin_info['metadata']['classifiers']:
        return True

    print("   >> SKIPPING - python version {}.{} not supported".format(
        python_version[0], python_version[1]))
    return False


def test_install():
    with open(PLUGINS_METADATA, 'r') as handle:
        data = json.load(handle)

    print("[test installing plugins]")
    for _k, v in six.iteritems(data):

        print(" - {}".format(v['name']))

        if not supports_python_version(v):
            continue

        # 'planning' plugins aren't installed/tested
        if v["development_status"] == 'planning':
            continue

        if 'pip_url' not in list(v.keys()):
            print("    >> WARNING: Missing pip_url key!")
            continue

        print("   - Installing {}".format(v['name']))
        is_installed = try_cmd("pip install {}".format(v['pip_url']))

        if not is_installed:
            continue

        if 'package_name' not in list(v.keys()):
            v['package_name'] = v['name'].replace('-', '_')

        print("   - Importing {}".format(v['package_name']))
        try_cmd("python -c 'import {}'".format(v['package_name']))
