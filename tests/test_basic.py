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
from pathlib import Path

import yaml

from aiida_registry.fetch_metadata import validate_plugin_entry_points
from aiida_registry.make_pages import get_pip_install_cmd
from aiida_registry.parse_build_file import (get_version_from_module,
                                             parse_flit_old, parse_pep_621,
                                             parse_poetry, parse_setup_cfg,
                                             parse_setup_json)

TEST_PATH = Path(__file__).parent / 'static'


def test_parse_setup_json(data_regression):
    """Test parsing setup.json file."""
    data = parse_setup_json((TEST_PATH / 'setup.json').read_text())
    data_regression.check(data.as_dict())


def test_parse_pyproject_toml_poetry(data_regression):
    """Test parsing pyproject.toml file."""
    data = parse_poetry((TEST_PATH / 'poetry-pyproject.toml').read_text())
    data_regression.check(data.as_dict())


def test_parse_pyproject_toml_flit_old(data_regression):
    """Test parsing pyproject.toml file."""
    data = parse_flit_old((TEST_PATH / 'flit-old-pyproject.toml').read_text())
    data_regression.check(data.as_dict())


def test_parse_pyproject_toml_pep621(data_regression):
    """Test parsing pyproject.toml file, that is PEP 621 compliant"""
    data = parse_pep_621((TEST_PATH / 'pep621-pyproject.toml').read_text())
    data_regression.check(data.as_dict())


def test_parse_setup_cfg(data_regression):
    """Test parsing pyproject.toml file."""
    data = parse_setup_cfg((TEST_PATH / 'setup.cfg').read_text())
    data_regression.check(data.as_dict())


def test_get_version_from_module():
    """Test parsing __version__ from module."""
    assert get_version_from_module('# comment\n__version__="0.0.1"') == '0.0.1'


def test_entrypoint_checks(capsys):
    """Test entry point checks of metadata.

    The registry should check only entry points from the 'aiida.' groups.
    """
    with open(TEST_PATH / 'plugins.yaml', 'r') as handle:
        test_data = yaml.safe_load(handle)

    # aiida-gulp example contains 'reaxff' entry point in 'gulp.potentials' group
    validate_plugin_entry_points(test_data['crystal17'])

    captured = capsys.readouterr()
    # should not warn about 'reaxff' not starting with 'gulp'
    assert 'reaxff' not in captured.out


def test_pip_install_cmd():
    """Test pip install command to display."""
    with open(TEST_PATH / 'plugins.yaml', 'r') as handle:
        test_data = yaml.safe_load(handle)

    # aiida-crystal17 is beta version
    assert '--pre' in get_pip_install_cmd(test_data['crystal17'])

    # aiida-core is stable version
    assert '--pre' not in get_pip_install_cmd(test_data['core'])
