# Available AiiDA Plugins

{% for plugin in plugins %}
## {{plugin.name}}

<dl>
<dt>Author:</dt><dd>{{plugin.author}}</dd>
<dt>Version:</dt><dd>{{plugin.version}}</dd>
</dl>

* Plugin home page: []({{plugin.home_url}})
* Base entry point: {{plugin.entry_point}}

Install command: `pip install {{plugin.pip_url}}``

Plugin code repository: []({{plugin.code_home}})

### Description: 

{{plugin.description}}

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
