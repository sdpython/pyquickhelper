{%- extends 'rst.tpl' -%}

{% block data_markdown %}
{{ output.data['text/markdown'] | convert_pandoc_rst("markdown", "rst") }}
{% endblock data_markdown %}

{% block data_svg %}
.. image:: {{ output.metadata.filenames['image/svg+xml'] | urlencode }}
{% endblock data_svg %}

{% block data_html scoped %}
{{ output.data['text/html'] | process_raw_html }}
{% endblock data_html %}
