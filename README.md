# AiiDA plugin registry

This repository contains the **source** of the official registry of AiiDA plugins.

<p align="center">
 <a href="http://aiidateam.github.io/aiida-registry" rel="Go to the AiiDA plugin registry">
  <img src="aiida_registry/static/gotobutton.svg">
 </a>
 </p>

If you are starting to develop a new plugin
(e.g. using the [AiiDA plugin cutter](https://github.com/aiidateam/aiida-plugin-cutter))
 or if you already have one, please register it here.
We strongly encourage to **register at early stages of development**,
since this both "reserves" the name of your plugin and informs the developer
community of your ongoing work.

By default, the list of plugins is now sorted by the latest release, so plugins that are under active development automatically bubble up to the top.
The release date is determined by the date of the latest [PyPI](https://pypi.org/) release. Plugins not released to PyPI will have no release date.

## How to register a plugin

1. Fork this repository
2. Add your plugin to the end of the `plugins.yaml` file, e.g.
    ```
    ...
    aiida-new:
      entry_point_prefix: new
      plugin_info: https://raw.github.com/aiidateam/aiida-new/master/setup.json
      code_home: https://github.com/aiidateam/aiida-new
      documentation_url: http://aiida-new.readthedocs.io/
    ```
3. Create a [Pull Request](https://github.com/aiidateam/aiida-registry/pulls) to this repository

### Valid keys for each plugin

#### top-level key (required)
The name under which your plugin will be distributed.
By convention, names of AiiDA plugins are lowercase and prefixed by `aiida-`.

Examples:
 * `aiida-quantumespresso`
 * `aiida-gaussian-datatypes`

#### entry_point_prefix (required)
The prefix of all entry points provided by the plugin.
By convention, a plugin `aiida-xxx` should use `entry_point_prefix: xxx`.

Example: `aiida-quantumespresso` uses the entry point prefix `quantumespresso` and provides numerous entry points, all of which start with `quantumespresso.`.

#### code_home (required)
The link to the homepage of the plugin, for example its github repository.

#### pip_url (required for development status `beta` and higher)
A URL or PyPI package name for installing the most recent version of the package through `pip`.

Examples:
 * `pip_url: aiida-quantumespresso` for a package that is [registered on PyPI](https://pypi.org/project/aiida-quantumespresso/)
 * `pip_url: git+https://github.com/aiidateam/aiida-wannier90` for a package not registered on PyPI

#### plugin_info (required for development status `stable`)
URL pointing to a JSON file containing the keyword arguments passed to the `setuptools.setup` function when installing your package.

For an example, see the [`setup.json`](https://github.com/aiidateam/aiida-diff/blob/master/setup.json) file of the [aiida-diff demo plugin](http://github.com/aiidateam/aiida-diff).

#### documentation_url (optional)
The link to the online documentation for your plugin, for example on readthedocs.org .

#### version_file (optional)

Use this to point to a Python module that contains a `__version__` variable with the version of your plugin.
Useful for `flit` and `setuptools` configuration files that use the programmatic `version = attr: aiida_plugin.__version__` format.
#### development_status (deprecated)
The development status of a plugin used to be recorded explicitly on the plugin registry.
Over time, we've moved closer and closer to adopting the [development status trove classifer](https://pypi.org/classifiers/), so we now suggest to just use those in your `setup.json`/`setup.cfg`/... file of your plugin.

If no development status is specified, the status will default to 'planning'.

## How to fix registry warnings and errors

You may want to check that your plugin is correctly registered before making the changes to your plugin repository.
To do so, you can run the registry check locally.

Clone this repository and install the dependencies:
```bash
git clone https://github.com/aiidateam/aiida-registry.git
pip install aiida-registry
```

Fetch the metadata and run installation test or your plugin
```bash
aiida-registry fetch-metadata <plugin-name>
aiida-registry test-install
```

You'll see the warnings and errors as what you can see from the registry page.

### Warning/Error codes

#### W001

- **Message**: Cannot fetch all data from PyPI and missing plugin_info key!
- **Cause**: The plugin is not registered on PyPI and the `plugin_info` key is missing.
- **Solution**: Register your plugin on PyPI or add the `plugin_info` key pointing to the correct plugin_info file.

#### W002

- **Message**: AiiDA version not found
- **Cause**: `aiida-core` is not found in the plugin requirements.
- **Solution**: Add `aiida-core` to the plugin requirements with the version specifier.

#### W003

- **Message**: Missing classifier 'Framework :: AiiDA'
- **Cause**: The plugin does not have the classifier `Framework :: AiiDA` in the plugin metadata (e.g. `setup.json`, `pyproject.toml`, `setup.cfg`).
- **Solution**: Add the classifier `Framework :: AiiDA` to the plugin metadata.

#### W004

- **Message**: Multiple development statuses found in classifiers
- **Cause**: The plugin has multiple development statuses in the plugin metadata.
- **Solution**: Remove the extra development status from the plugin metadata.

#### W005

- **Message**: Development status in classifiers not match development status in metadata
- **Cause**: The development status in the plugin metadata does not match the "developments_status" (deprecated, and defined in `plugins.yaml`).
- **Solution**: Use [development status trove classifer](https://pypi.org/classifiers/) only.

#### W006

- **Message**: `development_status` is deprecated.
- **Cause**: The `development_status` key is found in `plugins.yaml`.
- **Solution**: Use [development status trove classifer](https://pypi.org/classifiers/).

#### W007

- **Message**: Invalid development status.
- **Cause**: The development status is not one of the following: `planning`, `pre-alpha`, `alpha`, `beta`, `stable`, `mature`, `inactive`.
- **Solution**: Use one of the following development status: `planning`, `pre-alpha`, `alpha`, `beta`, `stable`, `mature`, `inactive`. But note that `development_status` is deprecated and you should use [development status trove classifer](https://pypi.org/classifiers/) instead.

#### W008

- **Message**: Unable to reach documentation URL.
- **Cause**: The documentation URL is not reachable.
- **Solution**: Check the documentation URL is correctly defined in `plugins.yaml`.

#### W009

- **Message**: Prefix of entry points does not follow naming convention.
- **Cause**: The prefix of entry points does not match the convention of package name, where if you have package `aiida-xxx`, the prefix of entry points should be `xxx`.
- **Solution**: Change the prefix of entry points to match the convention.

#### W010

- **Message**: Entry point does not start with proper prefix.
- **Cause**: The entry point does not start with the prefix defined in `plugins.yaml`.
- **Solution**: Change the entry point to start with the prefix defined in `plugins.yaml`.

#### W011

- **Message**: Unable to parse TOML.
- **Cause**: The `pyproject.toml` cannot be parsed.
- **Solution**: Check the `pyproject.toml` is correctly formatted.

#### W012

- **Message**: Unknown build system in `pyproject.toml`.
- **Cause**: The build system in `pyproject.toml` is not one of the following, check [PEP621](https://peps.python.org/pep-0621/): `setuptools`, `flit`, `poetry`.
- **Solution**: Use one of the following build system: `setuptools`, `flit`, `poetry`.

#### W013

- **Message**: Unknown build system.
- **Cause**: The build tool is not valid. We support setuptools (`setup.cfg`, `setup.json`), flit (`pyproject.toml`), poetry (`pyproject.toml`).
- **Solution**: Use one of the following build system: `setuptools`, `flit`, `poetry`.

#### W014

- **Message**: Unable to parse setup JSON.
- **Cause**: The `setup.json` cannot be parsed.
- **Solution**: Check the `setup.json` is correctly formatted.

#### W015

- **Message**: Version & description metadata are not (yet) parsed from the flit build system in `pyproject.toml`.
- **Cause**: The version & description metadata are not (yet) parsed from the flit build system in `pyproject.toml`.
- **Solution**: Add the version & description metadata to the `pyproject.toml`.

#### W016

- **Message**: Unable to parse `setup.cfg`.
- **Cause**: The `setup.cfg` cannot be parsed.
- **Solution**: Check the `setup.cfg` is correctly formatted.

#### W017

- **Message**: Invalid version encontered in Poery `pyproject.toml` for `aiida-core`.
- **Cause**: The version of `aiida-core` in `pyproject.toml` is not valid.
- **Solution**: Check the version of `aiida-core` in `pyproject.toml` is valid and correct.

#### W018

- **Message**: Unable to parse module of the package to futher parse the version from.
- **Cause**: The module of the package cannot be parsed.
- **Solution**: Check the module of the package is correctly formatted.

#### W019

- **Message**: No `bdist_wheel` available for PyPI release.
- **Cause**: The `bdist_wheel` is not available for PyPI release.
- **Solution**: Check the `bdist_wheel` is available for PyPI release.

#### W020

- **Message**: Unable to read wheel file from PyPI release.
- **Cause**: The wheel file cannot be read from PyPI release.
- **Solution**: Check the wheel file is correctly formatted.

#### E001

- **Message**: Failed to install the plugin
- **Cause**: The plugin cannot be installed with `pip install --pre`.
- **Solution**: Fix the installation of the plugin.

#### E002

- **Message**: Failed to import the plugin
- **Cause**: The plugin cannot be imported.
- **Solution**: Fix the import of the plugin.

#### E003

- **Message**: Failed to fetch entry point metadata for package
- **Cause**: The entry point metadata cannot be fetched.
- **Solution**: Check to see if the entry point metadata is correct.

#### E004

- **Message**: Unable to retrieve plugin metadata
- **Cause**: The plugin metadata cannot be retrieved.
- **Solution**: Check the URL of your plugin info URL in [plugins.yaml](plugins.yaml) is correct.
