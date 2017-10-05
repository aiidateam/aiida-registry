# Available AiiDA Plugins

{% for plugin in plugins %}
## {{plugin.name}}

<dl>
<dt>Author:</dt><dd>{{plugin.author}}</dd>
<dt>Version:</dt><dd>{{plugin.version}}</dd>
<dt>Plugin home page:</dt><dd>[]({{plugin.home_url}})</dd>
<dt>Base entry point:</dt><dd>{{plugin.entry_point}}</dd>
<dt>Install command:</dt><dd>`pip install {{plugin.pip_url}}``</dd>
<dt>Plugin code repository:</dt><dd>[]({{plugin.code_home}})</dd>
<dt>Description:</dt><dd>{{plugin.description}}</dd>
</dl>

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
