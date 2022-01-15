# -*- coding: utf-8 -*-
"""Module for parsing package build files."""
import ast
import json
from configparser import ConfigParser
from typing import Callable, List, NamedTuple, Optional

import requirements
import tomlkit
from poetry.core.semver import parse_constraint
from tomlkit.toml_document import TOMLDocument

from . import PLUGINS_METADATA_KEYS, REPORTER


class Data(NamedTuple):
    """Data read from the build file."""
    metadata: Optional[dict] = None
    entry_points: Optional[dict] = None
    aiida_version: Optional[str] = None

    def as_dict(self) -> dict:
        """Return a dictionary representation of the data."""
        return {
            'metadata': self.metadata,
            'entry_points': self.entry_points,
            'aiida_version': self.aiida_version,
        }


def identify_build_tool(url: str, content: str) -> Optional[str]:  # pylint: disable=too-many-return-statements
    """Identify the build tool, from the URL and content.

    - pyproject.toml (for poetry/flit and any PEP 621 compliant build tool)
    - setup.cfg (for setuptools)
    - setup.json (for setuptools)

    """
    if 'pyproject.toml' in url:
        try:
            pyproject = tomlkit.parse(content)
        except tomlkit.exceptions.TOMLKitError as exc:
            REPORTER.warn(f'Unable to parse TOML: {exc}')
            return None

        if 'project' in pyproject:
            return 'PEP621'

        tool_name = pyproject.get('tool', '')
        if 'poetry' in tool_name:
            return 'POETRY'
        if 'flit' in tool_name:
            return 'FLIT_OLD'

        REPORTER.warn(f'Unknown build system in pyproject.toml: {tool_name}')
        return None

    if 'setup.cfg' in url:
        return 'SETUPTOOLS_CFG'

    if 'setup.json' in url:
        return 'SETUPTOOLS_JSON'

    REPORTER.warn(f'Unknown build system: {url}')
    return None


def get_data_parser(name: str) -> Callable[[str, bool], Data]:
    """Return the function that parses the build file."""
    return {
        'PEP621': parse_pep_621,
        'SETUPTOOLS_JSON': parse_setup_json,
        'SETUPTOOLS_CFG': parse_setup_cfg,
        'POETRY': parse_poetry,
        'FLIT_OLD': parse_flit_old,
    }[name]


def parse_toml(content: str) -> Optional[TOMLDocument]:
    """Parse a TOML file."""
    try:
        return tomlkit.parse(content)
    except tomlkit.exceptions.TOMLKitError as exc:
        REPORTER.warn(f'Unable to parse TOML: {exc}')
    return None


def parse_pep_621(content: str, ep_only=False) -> Data:
    """Parse a https://www.python.org/dev/peps/pep-0621/ compliant pyproject.toml file."""
    data = parse_toml(content)
    if data is None:
        return Data()

    project_data = data.get('project', {})

    entry_points = project_data.get('entry-points', {}).copy()

    if ep_only:
        return Data(entry_points=entry_points)

    infos = {
        'aiida_version':
        get_aiida_version_list(project_data.get('dependencies', [])),
        'metadata': {
            k: project_data[k]
            for k in PLUGINS_METADATA_KEYS if k in project_data
        },
        'entry_points':
        entry_points,
    }
    infos['metadata']['classifiers'] = [
        str(c) for c in project_data.get('classifiers', [])
    ]
    if project_data.get('authors'):
        if 'name' in project_data['authors'][0]:
            infos['metadata']['author'] = str(
                project_data['authors'][0]['name'])
        if 'email' in project_data['authors'][0]:
            infos['metadata']['author_email'] = str(
                project_data['authors'][0]['email'])

    return Data(**infos)


def parse_setup_json(content: str, ep_only=False) -> Data:
    """Parse setup.json."""
    try:
        data = json.loads(content)
    except ValueError as exc:
        REPORTER.warn(f'Unable to parse JSON: {exc}')
        return Data()

    entry_points = {
        k: {v.split('=')[0].strip(): v.split('=')[1].strip()
            for v in g}
        for k, g in data.get('entry_points', {}).items()
    }

    if ep_only:
        return Data(entry_points=entry_points)

    infos = {
        'aiida_version':
        get_aiida_version_list(data.get('install_requires', [])),
        'metadata':
        {k: data[k] if k in data else ''
         for k in PLUGINS_METADATA_KEYS},
        'entry_points': entry_points,
    }
    infos['metadata']['classifiers'] = data.get('classifiers', [])

    return Data(**infos)


def parse_poetry(content: str, ep_only=False) -> Data:
    """Parse poetry pyproject.toml."""
    data = parse_toml(content)
    if data is None:
        return Data()

    entry_points = data['tool']['poetry'].get('plugins', {}).copy()

    if ep_only:
        return Data(entry_points=entry_points)

    infos = {
        'aiida_version': get_aiida_version_poetry(data),
        'metadata': {
            # all the following fields are mandatory in Poetry
            'version':
            str(data['tool']['poetry']['version']),
            'description':
            str(data['tool']['poetry']['description']),
            # the authors is a list of the strings of the form "name <email>"
            'author':
            ', '.join(
                a.split('<')[0].strip()
                for a in data['tool']['poetry']['authors']),
        },
        'entry_points': entry_points
    }
    infos['metadata']['classifiers'] = [
        str(item) for item in data['tool']['poetry'].get('classifiers', [])
    ]
    return Data(**infos)


def parse_flit_old(content: str, ep_only=False) -> Data:
    """Parse flit pyproject.toml with old-style metadata."""
    # uses https://flit.readthedocs.io/en/latest/pyproject_toml.html#old-style-metadata

    data = parse_toml(content)
    if data is None:
        return Data()

    entry_points = data['tool']['flit'].get('entrypoints', {}).copy()

    if ep_only:
        return Data(entry_points=entry_points)

    # version is not part of the metadata but expected to available in <module>/__init__.py:__version__
    # description is available as a reference in `description-file` (requires another fetch)
    # author is a mandatory field in Flit

    REPORTER.warn(
        'version & description metadata'
        ' are not (yet) parsed from the Flit buildsystem pyproject.toml')
    metadata = data['tool']['flit'].get('metadata', {})
    infos = {
        'aiida_version': get_aiida_version_list(metadata.get('requires', [])),
        'metadata': {
            'author': str(metadata.get('author', '')),
            'version': '',
            'description': '',
        },
        'entry_points': entry_points
    }
    return Data(**infos)


def parse_setup_cfg(content: str, ep_only=False) -> Data:
    """Parse setup.cfg."""

    try:
        config = ConfigParser()
        config.read_string(content)
    except Exception as exc:  # pylint: disable=broad-except
        REPORTER.warn(f'Unable to parse setup.cfg: {exc}')
        return Data()

    entry_points = {}
    if config.has_section('options.entry_points'):
        for name, values in config.items('options.entry_points'):
            entry_points[name] = {}
            for line in values.splitlines():
                if not line.strip() or line.strip().startswith('#'):
                    continue
                key, value = line.strip().split('=')
                entry_points[name][key.strip()] = value.strip()

    if ep_only:
        return Data(entry_points=entry_points)

    infos = {
        'aiida_version':
        get_aiida_version_list(
            config.get('options', 'install_requires').splitlines() if config.
            has_option('options', 'install_requires') else []),
        'metadata': {
            k: (config.get('metadata', k)
                if config.has_option('metadata', k) else '')
            for k in PLUGINS_METADATA_KEYS
        },
        'entry_points':
        entry_points
    }
    if config.has_option('metadata', 'classifiers'):
        infos['metadata']['classifiers'] = [
            l.strip()
            for l in config.get('metadata', 'classifiers').splitlines()
            if l.strip() and not l.strip().startswith('#')
        ]

    return Data(**infos)


def get_aiida_version_list(install_requires: List[str]) -> Optional[str]:
    """Get AiiDA version that this plugin is compatible with."""
    try:
        reqs = requirements.parse('\n'.join(install_requires))

        aiida_specs = []
        for req in reqs:
            # note: this also catches aiida-core[extra1]
            if req.name in ['aiida-core', 'aiida_core', 'aiida']:
                aiida_specs += req.specs

        if not aiida_specs:
            return None

        # precedence of version specs, from high to low
        precedence = ['==', '>=', '>', '<=', '<']
        sort_order = {precedence[i]: i for i in range(len(precedence))}
        aiida_specs = sorted(aiida_specs,
                             key=lambda r: sort_order.get(r[0], 10))

        # first index: operator (e,g, '>=')
        # second index: version (e.g. '0.12.0rc2')
        # In the future, this can be used to e.g. display a banner for 1.0-compatible plugins
        return ','.join([s[0] + s[1] for s in aiida_specs])

    except KeyError:
        return None


def get_aiida_version_poetry(pyproject):
    """Get AiiDA version that this plugin is compatible with from a pyproject.toml.
    """
    try:
        deps = pyproject['tool']['poetry']['dependencies']
    except KeyError:
        return None

    for name, data in deps.items():
        if name not in ['aiida-core', 'aiida_core', 'aiida']:
            continue

        try:  # data is either a dict {"version": ..., "extras": ["..", ], }
            version = data['version']
        except TypeError:  # or directly the version string
            version = data

        break
    else:
        return None

    try:
        return str(parse_constraint(version))
    except ValueError:
        REPORTER.warn(
            'Invalid version encountered in Poetry pyproject.toml for aiida-core'
        )

    return None


def get_version_from_module(content: str) -> Optional[str]:
    """Get the __version__ value from a module."""
    # adapted from setuptools/config.py
    try:
        module = ast.parse(content)
    except SyntaxError as exc:
        REPORTER.warn(f'Unable to parse module: {exc}')
        return None
    try:
        return next(
            ast.literal_eval(statement.value) for statement in module.body
            if isinstance(statement, ast.Assign)
            for target in statement.targets
            if isinstance(target, ast.Name) and target.id == '__version__')
    except StopIteration:
        return None
