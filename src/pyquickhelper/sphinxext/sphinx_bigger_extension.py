# -*- coding: utf-8 -*-
"""
@file
@brief Defines a sphinx extension to bigger text

.. versionadded:: 1.3
"""

import cgi
from docutils import nodes
from sphinx.writers.html import HTMLTranslator


class bigger_node(nodes.Element):

    """
    defines *sharenet* node
    """
    pass


def bigger_role(role, rawtext, text, lineno, inliner,
                options={}, content=[]):
    """
    Defines custom roles *bigger*. The following instructions defines
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
    what to do when visiting a node sharenet
    the function should have different behaviour,
    depending on the format, or the setup should
    specify a different function for each.
    """
    pass


def depart_bigger_node(self, node):
    """
    what to do when leaving a node sharenet
    the function should have different behaviour,
    depending on the format, or the setup should
    specify a different function for each.

    It does only html for the time being.
    """
    if not isinstance(self, HTMLTranslator):
        self.body.append("bigger: output only available for HTML")
        return

    self.body.append(
        '<font size="{1}">{0}</font>'.format(cgi.escape(node["text"]), node["size"]))
