# Registry for aiida plugins

Please register your in-development / stable plugins!

## How To

1. Fork the repository
2. Add your plugin
3. Create a Pull Request

### Keys

#### name
the name by which you will distribute the plugin (repository name, PYPI distribution name)

#### entry_point
The name which is at the beginning of all entry points the plugin exposes

#### state
One of
* registered: designates plugins which are not in a working state and may or may not have any code written. Use this to secure a specific name
* development: plugins which work partially but may not be stable yet
* stable: plugins which can be used in production. Note, that pull requests for 'stable' plugins will only be accepted after the aiida team verifies the usability.

#### pip_url
A url that can be used to directly install the most recent ('development') or most recent stable ('stable') version with pip.

#### plugin_info
A url pointing to a JSON file which holds all keyword args as given to the setuptools.setup function at install.

#### code_home
The homepage of your plugin.
