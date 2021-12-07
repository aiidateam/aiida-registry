# -*- coding: utf-8 -*-
"""
Tests of the AiiDA plugin registry code.

Note: Here we are testing the *code* of the registry, not validating actual entries.

Fetch metadata from plugins and dump it to temporary JSON file.

This fetches metadata from plugins defined using different build systems
 * setuptools/pip: setup.json
 * poetry: pyproject.toml
 * flit: pyproject.toml
"""
import json
from pathlib import Path

from aiida_registry.fetch_metadata import (get_version_from_module,
                                           parse_plugin_info,
                                           validate_plugin_entry_points)
from aiida_registry.make_pages import get_pip_install_cmd

TEST_PATH = Path(__file__).parent / 'static'


def test_parse_setup_json(data_regression):
    """Test parsing setup.json file."""
    data = parse_plugin_info('setup.json',
                             (TEST_PATH / 'setup.json').read_text())
    data_regression.check(data)


def test_parse_pyproject_toml_poetry(data_regression):
    """Test parsing pyproject.toml file."""
    data = parse_plugin_info('pyproject.toml',
                             (TEST_PATH / 'poetry-pyproject.toml').read_text())
    data_regression.check(data)


def test_parse_pyproject_toml_flit_old(data_regression):
    """Test parsing pyproject.toml file."""
    data = parse_plugin_info(
        'pyproject.toml', (TEST_PATH / 'flit-old-pyproject.toml').read_text())
    data_regression.check(data)


def test_parse_setup_cfg(data_regression):
    """Test parsing pyproject.toml file."""
    data = parse_plugin_info('setup.cfg',
                             (TEST_PATH / 'setup.cfg').read_text())
    data_regression.check(data)


def test_get_version_from_module():
    """Test parsing __version__ from module."""
    assert get_version_from_module('# comment\n__version__="0.0.1"') == '0.0.1'


def test_entrypoint_checks(capsys):
    """Test entry point checks of metadata.

    The registry should check only entry points from the 'aiida.' groups.
    """
    test_data = json.loads((TEST_PATH / 'plugins.json').read_text())

    # aiida-gulp example contains 'reaxff' entry point in 'gulp.potentials' group
    validate_plugin_entry_points(test_data['crystal17'])

    captured = capsys.readouterr()
    # should not warn about 'reaxff' not starting with 'gulp'
    assert 'reaxff' not in captured.out


def test_pip_install_cmd():
    """Test pip install command to display."""
    test_data = json.loads((TEST_PATH / 'plugins.json').read_text())

    # aiida-crystal17 is beta version
    assert '--pre' in get_pip_install_cmd(test_data['crystal17'])

    # aiida-core is stable version
    assert '--pre' not in get_pip_install_cmd(test_data['core'])
