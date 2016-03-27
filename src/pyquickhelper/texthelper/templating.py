"""
@file
@brief Templating functions
"""


class CustomTemplateException(Exception):
    """
    raised when a templatre could not compile
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
    """
    if engine == "mako":
        from mako.template import Template
        from mako.exceptions import CompileException
        try:
            tmpl = Template(text)
        except CompileException as ee:
            mes = ["%04d %s" % (i + 1, _)
                   for i, _ in enumerate(text.split("\n"))]
            raise CustomTemplateException("unable to compile\n" + "\n".join(mes)) from ee
        res = tmpl.render(**context)
        return res
    elif engine == "jinja2":
        from jinja2 import Template
        template = Template(text)
        return template.render(**context)
    else:
        raise ValueError("engine should be 'mako' or 'jinja2', not '{0}'".format(engine))
