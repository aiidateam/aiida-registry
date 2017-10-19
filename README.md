# Registry for aiida plugins

This is the official registry of AiiDA plugins, 
available at http://github.com/aiidateam/aiida-registry

If you are starting developing a new plugin or already have one,
please register it here.
It is a good idea to register your plugin as soon as you have a
clear plan of developing it, so you can "reserve" the name. 

## How To register a new plugin

1. Fork the repository
2. Add your plugin to the setup.json, with all needed information 
   specified (see below for the list of keys)
3. Create a Pull Request to this repository

### Valid keys for each plugin

#### name
the name by which you will distribute the plugin (repository name, PYPI distribution name)

#### entry_point
The name which is at the beginning of all entry points exposed by the plugin

#### state
One of
* registered: designates plugins which are not in a working state and may or may not have any code written. Use this to secure a specific name
* development: plugins which work partially but may not be stable yet
* stable: plugins which can be used in production. 

#### pip_url
A url that can be used to directly install the most recent ('development') or most recent stable ('stable') version with pip.

#### plugin_info
A url pointing to a JSON file which holds all keyword args as given to the setuptools.setup function at install (see also the example in the (aiida-plugin-template repository)[http://github.com/aiidateam/aiida-plugin-template].

#### code_home
The link to the homepage of your plugin (e.g. your website, or the github repository it is hosted on).

#### documentation_url
The link to the online documentation for your plugin (e.g. on Read The Docs).

