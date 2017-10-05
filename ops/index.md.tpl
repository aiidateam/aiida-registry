# Available AiiDA Plugins

{% for plugin in plugins %}
## {{plugin.name}}

{{plugin.description}}

```bash
pip install {{plugin.pip_url}}
```

* Author: {{plugin.author}}
* Version: {{plugin.version}}
* Plugin home page: []({{plugin.home_url}})
* Base entry point: {{plugin.entry_point}}
* Plugin code repository: []({{plugin.code_home}})


{# too much information?
### Plugin classes:
{% for category in plugin.entry_point_categories %}

#### {{category}}
{% for entry_point in plugin.entry_points[category] %}
* {{entry_point}}
{% endfor %}
{% endfor %}
#}
{% endfor %}
