#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test installing all registered plugins."""
from __future__ import absolute_import
from __future__ import print_function

import json
import six
import subprocess


def try_cmd(cmd):
    try:
        out = subprocess.check_output(cmd,
                                      shell=True,
                                      stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError:
        print(out)
        raise


with open('all_data.json', 'r') as handle:
    data = json.load(handle)

if __name__ == "__main__":

    print("[test installing plugins]")
    for k, v in six.iteritems(data['plugins']):
        print(" - Installing {}".format(v['name']))
        try_cmd("pip install {}".format(v['pip_url']))

        print(" - Importing {}".format(v['name']))
        try_cmd("python -c 'import {}'".format(v['package_name']))
