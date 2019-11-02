# -*- coding: utf-8 -*-
"""Fetch metadata from plugins and dump it to temporary JSON file.

This fetches metadata from plugins defined using different build systems
 * setuptools/pip: setup.json
 * poetry: pyproject.toml
 * flit: pyproject.toml
"""
from __future__ import absolute_import
from __future__ import print_function


def test_entrypoint(capsys):
    """Test entry point checks.

    The registry should check only entry points from the 'aiida.' groups.
    """
    from . import TEST_DATA
    from aiida_registry.fetch_metadata import validate_plugin_entry_points

    # aiida-gulp example contains 'reaxff' entry point in 'gulp.potentials' group
    validate_plugin_entry_points(TEST_DATA['crystal17'])

    captured = capsys.readouterr()
    # should not warn about 'reaxff' not starting with 'gulp'
    assert 'reaxff' not in captured.out
