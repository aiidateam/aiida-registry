#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test installing all registered plugins."""
from __future__ import absolute_import
from __future__ import print_function

import json
import six
import subprocess
import os

pwd = os.path.split(os.path.abspath(__file__))[0]
PLUGINS_FILE_ABS = os.path.join(pwd, os.pardir, 'plugins.json')


def try_cmd(cmd):
    try:
        return subprocess.check_output(cmd,
                                       shell=True,
                                       stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as exc:
        print(exc.output)
        return False


with open(PLUGINS_FILE_ABS, 'r') as handle:
    data = json.load(handle)

if __name__ == "__main__":

    print("[test installing plugins]")
    for k, v in six.iteritems(data):

        print(" - {}".format(v['name']))

        # 'registered' plugins aren't installed/tested
        if v['state'] == 'registered':
            continue

        if 'pip_url' not in list(v.keys()):
            print("  >> WARNING: Missing pip_url key!")
            continue

        print(" - Installing {}".format(v['name']))
        is_installed = try_cmd("pip install {}".format(v['pip_url']))

        if not is_installed:
            continue

        if 'package_name' not in list(v.keys()):
            v['package_name'] = v['name'].replace('-', '_')

        print(" - Importing {}".format(v['package_name']))
        try_cmd("python -c 'import {}'".format(v['package_name']))
