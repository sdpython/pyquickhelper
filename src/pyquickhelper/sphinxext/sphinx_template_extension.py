# -*- coding: utf-8 -*-
"""
@file
@brief Defines a sphinx extension ``tpl``, a role which use templating.
"""

import sphinx
from docutils import nodes
from ..texthelper import apply_template


class tpl_node(nodes.TextElement):

    """
    Defines *tpl* node.
    """
    pass


class ClassStruct:
    """
    Class as struct.
    """

    def __init__(self, **kwargs):
        """
        All arguments are added to the class.
        """
        for k, v in kwargs.items():
            setattr(self, k, v)


def evaluate_template(template, engine="jinja2", **kwargs):
    """
    Evaluate a template given a list of parameters given
    a list of named parameters.

    @param      template        template (:epkg:`jinja2`)
    @param      engine          :epkg:`jinja2` or :epkg:`mako`
    @param      kwargs          additional parameters
    @return                     outcome

    The function uses @see fn apply_template.
    """
    return apply_template(template, context=kwargs, engine=engine)


def tpl_role(role, rawtext, text, lineno, inliner, options=None, content=None):
    """
    Defines custom role *tpl*. A template must be specified in
    the configuration file.

    ::

        :tpl:`template_name,p1=v2, p2=v2, ...`

    The role evaluate this expression with function :epkg:`*pyf:eval`:

    ::

        evaluate_template(template, p1=v1, p2=v2, ...)

    You can switch engine by adding parameter ``engine='mako'``.
    In the configuration file, the following must be added:

    ::

        tpl_template = {'template_name': 'some template'}

    ``template_name`` can also be a function.

    ::

        tpl_template = {'py': python_link_doc}

    And the corresponding line in the documentation:

    ::

        :tpl:`py,m='ftplib',o='FTP.storbinary'`

    Which gives: :tpl:`py,m='ftplib',o='FTP.storbinary'` based on
    function :func:`python_link_doc <pyquickhelper.sphinxext.documentation_link.python_link_doc>`.

    :param role: The role name used in the document.
    :param rawtext: The entire markup snippet, with role.
    :param text: The text marked with the role.
    :param lineno: The line number where rawtext appears in the input.
    :param inliner: The inliner instance that called us.
    :param options: Directive options for customization.
    :param content: The directive content for customization.
    """
    spl = text.split(",")
    template_name = spl[0]
    if len(spl) == 1:
        context = ""
    else:
        context = ",".join(spl[1:])

    env = inliner.document.settings.env
    app = env.app
    config = app.config

    try:
        tpl_template = config.tpl_template
    except AttributeError as e:  # pragma: no cover
        ma = "\n".join(sorted(str(_) for _ in app.config))
        raise AttributeError(
            "unable to find 'tpl_template' in configuration. Available:\n{0}".format(ma)) from e

    if template_name not in tpl_template:
        keys = "\n".join(sorted(tpl_template))  # pragma: no cover
        raise ValueError(  # pragma: no cover
            "Unable to find template '{0}' in tpl_template. Found:\n{1}".format(template_name, keys))
    tpl_content = tpl_template[template_name]

    code = "dict(" + context + ")"
    try:
        val_context = eval(code)
    except Exception as e:  # pragma: no cover
        raise Exception(  # pragma: no cover
            "Unable to compile '''{0}'''".format(code)) from e

    if isinstance(tpl_content, str):
        res = evaluate_template(tpl_content, **val_context)
    else:
        res = tpl_content(**val_context)

    node = tpl_node(rawtext=rawtext)
    node['classes'] += ["tpl"]

    memo = ClassStruct(document=inliner.document, reporter=inliner.reporter,
                       language=inliner.language)
    processed, messages = inliner.parse(res, lineno, memo, node)
    if len(messages) > 0:
        msg = inliner.reporter.error(
            "unable to interpret '{0}', messages={1}".format(
                text, ", ".join(str(_) for _ in messages)), line=lineno)
        prb = inliner.problematic(rawtext, rawtext, msg)
        return [prb], [msg]

    node += processed
    return [node], []


def visit_tpl_node(self, node):
    """
    What to do when visiting a node *tpl*.
    """
    pass


def depart_tpl_node(self, node):
    """
    What to do when leaving a node *tpl*.
    """
    pass


def setup(app):
    """
    setup for ``bigger`` (sphinx)
    """
    if hasattr(app, "add_mapping"):
        app.add_mapping('tpl', tpl_node)

    app.add_config_value('tpl_template', {}, 'env')
    app.add_node(tpl_node,
                 html=(visit_tpl_node, depart_tpl_node),
                 epub=(visit_tpl_node, depart_tpl_node),
                 elatex=(visit_tpl_node, depart_tpl_node),
                 latex=(visit_tpl_node, depart_tpl_node),
                 rst=(visit_tpl_node, depart_tpl_node),
                 md=(visit_tpl_node, depart_tpl_node),
                 text=(visit_tpl_node, depart_tpl_node))

    app.add_role('tpl', tpl_role)
    return {'version': sphinx.__display_version__, 'parallel_read_safe': True}
