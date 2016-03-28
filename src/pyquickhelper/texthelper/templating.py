"""
@file
@brief Templating functions

.. versionadded:: 1.4
"""


class CustomTemplateException(Exception):
    """
    raised when a templatre could not compile

    .. versionadded:: 1.4
    """
    pass


def apply_template(text, context, engine="mako"):
    """
    Extend a string containing templating instructions.
    See `mako <http://www.makotemplates.org/>`_ or
    `jinja2 <http://jinja.pocoo.org/docs/dev/>`_.

    @param      text        text
    @param      context     local variable to use
    @param      engine      'mako' or 'jinja2'
    @return                 resulting text

    .. versionadded:: 1.4
    """
    if engine == "mako":
        from mako.template import Template
        from mako.exceptions import CompileException
        try:
            tmpl = Template(text)
        except CompileException as ee:
            mes = ["%04d %s" % (i + 1, _)
                   for i, _ in enumerate(text.split("\n"))]
            raise CustomTemplateException(
                "unable to compile with mako\n" + "\n".join(mes)) from ee
        res = tmpl.render(**context)
        return res
    elif engine == "jinja2":
        from jinja2 import Template
        from jinja2.exceptions import TemplateSyntaxError
        try:
            template = Template(text)
        except TemplateSyntaxError as eee:
            mes = ["%04d %s" % (i + 1, _)
                   for i, _ in enumerate(text.split("\n"))]
            raise CustomTemplateException(
                "unable to compile with jinja2\n" + "\n".join(mes)) from eee
        res = template.render(**context)
        return res
    else:
        raise ValueError(
            "engine should be 'mako' or 'jinja2', not '{0}'".format(engine))
