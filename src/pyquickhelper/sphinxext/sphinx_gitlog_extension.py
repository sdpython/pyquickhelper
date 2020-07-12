# -*- coding: utf-8 -*-
"""
@file
@brief Defines a :epkg:`sphinx` extension to display gitlog text.
"""
from datetime import datetime
import sphinx
from docutils import nodes
from sphinx.util.logging import getLogger


class gitlog_node(nodes.Element):

    """
    Defines *gitlog* node.
    """
    pass


def gitlog_role(role, rawtext, text, lineno, inliner, options=None, content=None):
    """
    Defines custom role *gitlog*. The following instruction prints
    out the date of the last modification for the current file.

    ::

        :gitlog:`date`

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
    node = gitlog_node(text=text)
    node['classes'] += ["gitlog"]
    if text == 'date':
        source = inliner.document.current_source
        if source == '<string>':
            value = str(datetime.now())
        else:
            from ..loghelper.repositories.pygit_helper import get_file_last_modification
            value = get_file_last_modification(source)
        node['text'] = value
    elif text.startswith('date:'):
        source = text[5:]
        from ..loghelper.repositories.pygit_helper import get_file_last_modification
        value = get_file_last_modification(source)
        node['text'] = value
    else:
        raise ValueError(  # pragma: no cover
            "Unable to interpret this instuction '{}'.".format(text))
    return [node], []


def depart_gitlog_node_html(self, node):
    """
    what to do when leaving a node *gitlog*
    the function should have different behaviour,
    depending on the format, or the setup should
    specify a different function for each.

    It does only html for the time being.
    """
    self.body.append(node["text"])


def visit_gitlog_node_rst(self, node):
    """
    what to do when visiting a node *gitlog*
    the function should have different behaviour,
    depending on the format, or the setup should
    specify a different function for each.
    """
    self.add_text(':gitlog:`')
    self.add_text(node["text"])


def depart_gitlog_node_rst(self, node):
    """
    depart *gitlog_node* for rst
    """
    self.add_text('`')


def visit_gitlog_node_latex(self, node):
    """
    what to do when visiting a node *gitlog*
    the function should have different behaviour,
    depending on the format, or the setup should
    specify a different function for each.
    """
    self.add_text(node["text"])


def depart_gitlog_node_latex(self, node):
    """
    depart *gitlog_node* for latex
    """


def visit_gitlog_node(self, node):
    """
    what to do when visiting a node *gitlog*
    the function should have different behaviour,
    depending on the format, or the setup should
    specify a different function for each.
    """
    pass


def depart_gitlog_node(self, node):
    """
    depart *gitlog_node* for format other than html
    """
    logger = getLogger("gitlog")
    logger.warning("[depart_gitlog_node] output only available for HTML not for '{0}'".format(
        type(self)))


def setup(app):
    """
    setup for ``gitlog`` (sphinx)
    """
    if hasattr(app, "add_mapping"):
        app.add_mapping('gitlog', gitlog_node)

    app.add_node(gitlog_node,
                 html=(visit_gitlog_node, depart_gitlog_node_html),
                 epub=(visit_gitlog_node, depart_gitlog_node_html),
                 latex=(visit_gitlog_node_latex, depart_gitlog_node_latex),
                 elatex=(visit_gitlog_node_latex, depart_gitlog_node_latex),
                 text=(visit_gitlog_node, depart_gitlog_node),
                 md=(visit_gitlog_node, depart_gitlog_node),
                 rst=(visit_gitlog_node_rst, depart_gitlog_node_rst))

    app.add_role('gitlog', gitlog_role)
    return {'version': sphinx.__display_version__, 'parallel_read_safe': True}
