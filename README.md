# AiiDA plugin registry

This repository contains the source of the official registry of AiiDA plugins.

To visit the registry, pleas click on the button below.

<div class="bigGreenButton"> <a href="http://aiidateam.github.io/aiida-registry" style="display: inline-block; font-family: Verdana, sans-serif; font-size:18px; background-color:#60a74a; color:white; padding-bottom:10px; padding-top:10px; padding-left:25px; padding-right:25px; text-decoration:none; height:auto; width:auto; text-align:center; border-radius: 6px;">Go to the AiiDA plugin registry!<br />
<span style="font-size: 80%; text-color='#9f9';">http://aiidateam.github.io/aiida-registry</span>
</a></div>

If you are starting to develop a new plugin
(e.g. using the [AiiDA plugin cutter](https://github.com/aiidateam/aiida-plugin-cutter))
 or if you already have one, please register it here.
We strongly encourage to **register at early stages of development**,
since this both "reserves" the name of your plugin and informs the developer
community of your ongoing work.

## How to register a plugin

1. Fork the repository
2. Add your plugin to the `plugins.json` file, e.g. 
    ```
    "new": {
        "name": "aiida-new",
        "entry_point": "new",
        "state": "development",
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
The name which is at the beginning of all entry points exposed by the plugin

#### state
One of
* `registered`: designates plugins which are not in a working state and may or may not have any code written. Use this to secure a specific name
* `development`: plugins which work partially but may not be stable yet
* `stable`: plugins which can be used in production. 

#### pip_url
A url that can be used to directly install the most recent ('development') or most recent stable ('stable') version with pip.

#### plugin_info
A URL pointing to a JSON file which holds all keyword args, as given to the setuptools.setup function at install.
See, for example, the [aiida-plugin-template repository](http://github.com/aiidateam/aiida-plugin-template).

#### code_home
The link to the homepage of your plugin (e.g. your website, or the github repository it is hosted on).

#### documentation_url
The link to the online documentation for your plugin (e.g. on Read The Docs).
