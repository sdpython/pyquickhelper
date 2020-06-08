"""
@file
@brief Templating functions
"""
from pprint import pformat


class CustomTemplateException(Exception):
    """
    Raised when a templatre could not compile.
    """
    pass


def apply_template(text, context, engine="mako"):
    """
    Extend a string containing templating instructions.
    See :epkg:`mako` or :epkg:`jinja2`.

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
            import mako.exceptions
            exc = mako.exceptions.text_error_template()
            text = exc.render()
            raise CustomTemplateException(
                "unable to compile with mako\n{0}\nCODE:\n{1}".format(text, "\n".join(mes))) from ee
        try:
            res = tmpl.render(**context)
        except Exception as ee:
            import mako.exceptions
            exc = mako.exceptions.text_error_template()
            text = exc.render()
            raise CustomTemplateException(
                "Some parameters are missing or mispelled.\n" + text) from ee
        return res
    elif engine == "jinja2":
        from jinja2 import Template
        from jinja2.exceptions import TemplateSyntaxError, UndefinedError
        try:
            template = Template(text)
        except TemplateSyntaxError as eee:
            mes = ["%04d %s" % (i + 1, _)
                   for i, _ in enumerate(text.split("\n"))]
            raise CustomTemplateException(
                "unable to compile with jinja2\n" + "\n".join(mes)) from eee
        try:
            res = template.render(**context)
        except UndefinedError as ee:
            raise CustomTemplateException(
                "Some parameters are missing or mispelled\n{}"
                "".format(pformat(context))) from ee
        return res
    else:
        raise ValueError(  # pragma: no cover
            "engine should be 'mako' or 'jinja2', not '{0}'".format(engine))
