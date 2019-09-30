# AiiDA plugin registry

This repository contains the **source** of the official registry of AiiDA plugins.

<p align="center">
 <a href="http://aiidateam.github.io/aiida-registry" rel="Go to the AiiDA plugin registry">
  <img src="make_ghpages/static/gotobutton.svg">
 </a>
 </p>

If you are starting to develop a new plugin
(e.g. using the [AiiDA plugin cutter](https://github.com/aiidateam/aiida-plugin-cutter))
 or if you already have one, please register it here.
We strongly encourage to **register at early stages of development**,
since this both "reserves" the name of your plugin and informs the developer
community of your ongoing work.

## How to register a plugin

1. Fork this repository
2. Add your plugin to the `plugins.json` file, e.g.
    ```
    "new": {
        "name": "aiida-new",
        "entry_point": "new",
        "state": "registered",
        "plugin_info": "https://raw.github.com/aiidateam/aiida-new/master/setup.json",
        "code_home": "https://github.com/aiidateam/aiida-new",
        "documentation_url": "http://aiida-new.readthedocs.io/"
    },
    ```
3. Create a [Pull Request](https://github.com/aiidateam/aiida-registry/pulls) to this repository

### Valid keys for each plugin

#### name
the name by which you will distribute the plugin (repository name, PYPI distribution name)

#### entry_point
The name which is at the beginning of all entry points exposed by the plugin.

Convention: A plugin `aiida-quantumespresso` should use `entry_point: 'quantumespresso'`.

#### state
One of
* `registered`: plugin is not yet in a working state. Use this to secure a specific name before starting development
* `development`: plugin adds new functionality but isn't stable enough for production use
* `stable`: plugin can be used in production

#### pip_url
A URL or PyPI package name for installing the most recent development (`state: 'development'`) or stable (`state: 'stable'`) version of the package with pip.
Expected for states `development` and `stable`.

Examples:
 * `"pip_url": "aiida-quantumespresso"` for a package that is [registered on PyPI](https://pypi.org/project/aiida-quantumespresso/)
 * `"pip_url": "git+https://github.com/aiidateam/aiida-wannier90"` for a package not registered on PyPI

#### plugin_info
A URL pointing to a JSON file which holds all keyword args, as given to the setuptools.setup function at install.
See, for example, the [aiida-plugin-template repository](http://github.com/aiidateam/aiida-plugin-template).

#### code_home
The link to the homepage of your plugin (e.g. your website, or the github repository it is hosted on).

#### documentation_url
The link to the online documentation for your plugin (e.g. on Read The Docs).
