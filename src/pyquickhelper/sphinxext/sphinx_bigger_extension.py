# -*- coding: utf-8 -*-
"""
@file
@brief Defines a sphinx extension to display bigger text

.. versionadded:: 1.3
"""

import sys
import sphinx
from docutils import nodes
from sphinx.writers.html import HTMLTranslator


if sys.version_info[0] == 2:
    import cgi as cgiesc
else:
    import html as cgiesc


class bigger_node(nodes.Element):

    """
    defines *bigger* node
    """
    pass


def bigger_role(role, rawtext, text, lineno, inliner,
                options={}, content=[]):
    """
    Defines custom role *bigger*. The following instructions defines
    buttons of size 20 (:bigger:`text`)::

        :bigger:`text`

    Or to specify a different :bigger:`::5:size` ::

        :bigger:`::5:size`

    :param name: The role name used in the document.
    :param rawtext: The entire markup snippet, with role.
    :param text: The text marked with the role.
    :param lineno: The line number where rawtext appears in the input.
    :param inliner: The inliner instance that called us.
    :param options: Directive options for customization.
    :param content: The directive content for customization.
    """
    if text.startswith("::"):
        size, text = text[2:].split(':')
    else:
        size = "4"
    node = bigger_node(text=text, size=size)
    node['classes'] += "-bigger"
    node['bigger'] = node
    return [node], []


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
    what to do when leaving a node *bigger*
    the function should have different behaviour,
    depending on the format, or the setup should
    specify a different function for each.

    It does only html for the time being.
    """
    if not isinstance(self, HTMLTranslator):
        self.body.append("%bigger: output only available for HTML\n")
        return

    self.body.append(
        '<font size="{1}">{0}</font>'.format(cgiesc.escape(node["text"]), node["size"]))


def setup(app):
    """
    setup for ``bigger`` (sphinx)
    """
    if hasattr(app, "add_mapping"):
        app.add_mapping('bigger', bigger_node)

    app.add_node(bigger_node,
                 html=(visit_bigger_node, depart_bigger_node),
                 latex=(visit_bigger_node, depart_bigger_node),
                 text=(visit_bigger_node, depart_bigger_node))

    app.add_role('bigger', bigger_role)
    return {'version': sphinx.__display_version__, 'parallel_read_safe': True}
