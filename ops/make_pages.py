from __future__ import print_function
import json
import os
import re

import jinja2

from aiida.plugins import registry
from aiida.plugins import info

def warning_error_handler(err, plugin=None, data=None):
    print(repr(err))


BASE_FOLDER = os.path.dirname(os.path.abspath(__file__))


if __name__ == '__main__':
    registry.update(registry_err_handler=warning_error_handler, info_err_handler=warning_error_handler)

    pat = re.compile('.*')
    all_plugins = info.find_by_pattern(pat)

    template = jinja2.Environment(
        loader=jinja2.FileSystemLoader(
            BASE_FOLDER)).get_template('index.md.tpl')

    with open(os.path.join(BASE_FOLDER, '..', 'index.md'), 'w') as index_f:
        content = template.render(plugins=all_plugins)
        index_f.write(content.encode('utf-8'))
