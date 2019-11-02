# -*- coding: utf-8 -*-
"""Tests of the AiiDA plugin registry code.

Note: Here we are testing the *code* of the registry, not validating actual entries.
"""

from __future__ import absolute_import
from __future__ import print_function
import os
import json

# Absolute paths
pwd = os.path.split(os.path.abspath(__file__))[0]
TEST_DATA_ABS = os.path.join(pwd, 'test_metadata.json')

with open(TEST_DATA_ABS) as f:
    TEST_DATA = json.load(f)
