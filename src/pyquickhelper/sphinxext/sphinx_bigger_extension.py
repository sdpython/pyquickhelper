# -*- coding: utf-8 -*-
"""
@file
@brief Defines a :epkg:`sphinx` extension to display bigger text.
"""
import html as cgiesc
import sphinx
from docutils import nodes
from sphinx.util.logging import getLogger


class bigger_node(nodes.Element):

    """
    Defines *bigger* node.
    """
    pass


def bigger_role(role, rawtext, text, lineno, inliner, options=None, content=None):
    """
    Defines custom role *bigger*. The following instructions defines
    buttons of size 20 (:bigger:`text`):

    ::

        :bigger:`text`

    Or to specify a different :bigger:`::5:size` :

    ::

        :bigger:`::5:size`

    :param role: The role name used in the document.
    :param rawtext: The entire markup snippet, with role.
    :param text: The text marked with the role.
    :param lineno: The line number where rawtext appears in the input.
    :param inliner: The inliner instance that called us.
    :param options: Directive options for customization.
    :param content: The directive content for customization.
    """
    if options is None:
        options = {}
    if content is None:
        content = []
    if text.startswith("::"):
        size, text = text[2:].split(':')
    else:
        size = "4"
    node = bigger_node(text=text, size=size)
    node['classes'] += ["bigger"]
    return [node], []


def depart_bigger_node_html(self, node):
    """
    what to do when leaving a node *bigger*
    the function should have different behaviour,
    depending on the format, or the setup should
    specify a different function for each.

    It does only html for the time being.
    """
    self.body.append(
        '<font size="{1}">{0}</font>'.format(cgiesc.escape(node["text"]), node["size"]))


def visit_bigger_node_rst(self, node):
    """
    what to do when visiting a node *bigger*
    the function should have different behaviour,
    depending on the format, or the setup should
    specify a different function for each.
    """
    self.add_text(':bigger:`')
    self.add_text(node["text"])


def depart_bigger_node_rst(self, node):
    """
    depart bigger_node for rst
    """
    self.add_text('`')


def visit_bigger_node_latex(self, node):
    """
    what to do when visiting a node *bigger*
    the function should have different behaviour,
    depending on the format, or the setup should
    specify a different function for each.
    """
    self.add_text('\\huge{')
    self.add_text(node["text"])


def depart_bigger_node_latex(self, node):
    """
    depart bigger_node for latex
    """
    self.add_text('}')


def visit_bigger_node(self, node):
    """
    what to do when visiting a node *bigger*
    the function should have different behaviour,
    depending on the format, or the setup should
    specify a different function for each.
    """
    pass


def depart_bigger_node(self, node):
    """
    depart bigger_node for format other than html
    """
    logger = getLogger("bigger")
    logger.warning("[depart_bigger_node] output only available for HTML not for '{0}'".format(
        type(self)))


def setup(app):
    """
    setup for ``bigger`` (sphinx)
    """
    if hasattr(app, "add_mapping"):
        app.add_mapping('bigger', bigger_node)

    app.add_node(bigger_node,
                 html=(visit_bigger_node, depart_bigger_node_html),
                 epub=(visit_bigger_node, depart_bigger_node_html),
                 latex=(visit_bigger_node_latex, depart_bigger_node_latex),
                 elatex=(visit_bigger_node_latex, depart_bigger_node_latex),
                 text=(visit_bigger_node, depart_bigger_node),
                 md=(visit_bigger_node, depart_bigger_node),
                 rst=(visit_bigger_node_rst, depart_bigger_node_rst))

    app.add_role('bigger', bigger_role)
    return {'version': sphinx.__display_version__, 'parallel_read_safe': True}
