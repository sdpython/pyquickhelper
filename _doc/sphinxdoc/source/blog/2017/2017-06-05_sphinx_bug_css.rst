
.. blogpost::
    :title: Bug in Sphinx 1.6.2 for custom css
    :keywords: documentation, sphinx, bug
    :date: 2017-06-05
    :categories: documentation
    :lid: sphinx-162-bug-custom-css

    I was finally able to take some time and finish
    the migration to *Sphinx 1.6.2*. However,
    there is still an error I cannot fix because it
    is a bug in Sphinx which happens when a custom css is used.

    ::

        jinja2.exceptions.UndefinedError: 'str object' has no attribute 'filename'

    The bug is fixed in the current developpment version
    by this commit:
    `Check css.rel attributes to test str or Stylesheet object <https://github.com/sphinx-doc/sphinx/commit/927a760e0c11df8aa6b0bba89debd097611293aa>`_
    and I did not find any better way than modifying the file
    ``sphinx/theme/basic/layout.html`` and by updating the following block:

    ::

        {%- macro css() %}
        <link rel="stylesheet" href="{{ pathto('_static/' + style, 1) }}" type="text/css" />
        <link rel="stylesheet" href="{{ pathto('_static/pygments.css', 1) }}" type="text/css" />
        {%- for css in css_files %}
          {%- if css|attr("rel") %}
        <link rel="{{ css.rel }}" href="{{ pathto(css.filename, 1) }}" type="text/css"{% if css.title is not none %} title="{{ css.title }}"{% endif %} />
          {%- else %}
        <link href="{{ pathto(css, 1) }}" type="text/css" />
          {%- endif %}
        {%- endfor %}
        {%- endmacro %}

    This is really annoying. This probably means there is no
    unit test covering this functionality.
