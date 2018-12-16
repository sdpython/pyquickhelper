# -*- coding: utf-8 -*-
"""
@file
@brief Defines a :epkg:`sphinx` extension for a quote.
"""
from docutils import nodes
from docutils.parsers.rst import directives

import sphinx
from sphinx.locale import _
from docutils.parsers.rst.directives.admonitions import BaseAdmonition
from docutils.statemachine import StringList
from sphinx.util.nodes import nested_parse_with_titles


class quote_node(nodes.admonition):
    """
    Defines ``quote`` node.
    """
    pass


class QuoteNode(BaseAdmonition):
    """
    A ``quotedef`` entry, displayed in the form of an admonition.
    It takes the following options:

    * *author*
    * *book*
    * *year*
    * *pages*
    * *tag*
    * *lid*
    * *label*

    Example::

        .. quotedef::
            :author: author
            :book: book
            :year: year
            :pages: pages (optional)
            :tag: something
            :lid: id (used for further reference)

            A monkey could...
    """

    node_class = quote_node
    has_content = True
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {
        'author': directives.unchanged,
        'book': directives.unchanged,
        'year': directives.unchanged,
        'pages': directives.unchanged,
        'tag': directives.unchanged,
        'lid': directives.unchanged,
        'label': directives.unchanged,
        'class': directives.class_option,
    }

    def run(self):
        """
        Builds the mathdef text.
        """
        lineno = self.lineno

        env = self.state.document.settings.env if hasattr(
            self.state.document.settings, "env") else None
        docname = None if env is None else env.docname
        if docname is not None:
            docname = docname.replace("\\", "/").split("/")[-1]

        if not self.options.get('class'):
            self.options['class'] = ['admonition-quote']

        # body
        (quote,) = super(QuoteNode, self).run()
        if isinstance(quote, nodes.system_message):
            return [quote]

        # mid
        tag = self.options.get('tag', 'quotetag').strip()
        if len(tag) == 0:
            raise ValueError("tag is empty")
        if env is not None:
            mid = int(env.new_serialno('indexquote-u-%s' % tag)) + 1
        else:
            mid = -1

        # book
        author = _(self.options.get('author', "").strip())
        book = _(self.options.get('book', "").strip())
        pages = _(self.options.get('pages', "").strip())
        year = _(self.options.get('year', "").strip())

        # add a label
        lid = self.options.get('lid', self.options.get('label', None))
        if lid:
            tnl = [".. _{0}:".format(lid), ""]
        else:
            tnl = []

        if author:
            tnl.append("**{0}**, ".format(author))
        if book:
            tnl.append("*{0}*, ".format(book))
        if pages:
            tnl.append("{0} ".format(pages))
        if year:
            tnl.append("({0}), ".format(year))
        else:
            tnl.append(", ")

        content = StringList(tnl)
        content = content + self.content
        node = quote_node()

        try:
            nested_parse_with_titles(self.state, content, node)
        except Exception as e:
            from sphinx.util import logging
            logger = logging.getLogger("blogpost")
            logger.warning(
                "[blogpost] unable to parse '{0}' - '{1}' - {2}".format(author, book, e))
            raise e

        quote['tag'] = tag
        quote['author'] = author
        quote['pages'] = pages
        quote['year'] = year
        node['classes'] += ["quote"]

        return [node]


def visit_quote_node(self, node):
    """
    visit_quote_node
    """
    self.visit_admonition(node)


def depart_quote_node(self, node):
    """
    depart_quote_node,
    see https://github.com/sphinx-doc/sphinx/blob/master/sphinx/writers/html.py
    """
    self.depart_admonition(node)


def setup(app):
    """
    setup for ``mathdef`` (sphinx)
    """
    if hasattr(app, "add_mapping"):
        app.add_mapping('quote', quote_node)

    app.add_node(quote_node,
                 html=(visit_quote_node, depart_quote_node),
                 epub=(visit_quote_node, depart_quote_node),
                 elatex=(visit_quote_node, depart_quote_node),
                 latex=(visit_quote_node, depart_quote_node),
                 text=(visit_quote_node, depart_quote_node),
                 md=(visit_quote_node, depart_quote_node),
                 rst=(visit_quote_node, depart_quote_node))

    app.add_directive('quote', QuoteNode)
    return {'version': sphinx.__display_version__, 'parallel_read_safe': True}
