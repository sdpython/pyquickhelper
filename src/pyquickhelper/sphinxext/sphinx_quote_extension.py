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
    * *source*
    * *lid* or *label*
    * *index*, additional index words beside the title and the author
    * *date*, if the text was written or declared at specific date

    Example::

        .. quote::
            :author: author
            :book: book
            :year: year
            :pages: pages (optional)
            :tag: something
            :lid: id (used for further reference)
            :source: optional
            :index: word

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
        'source': directives.unchanged,
        'class': directives.class_option,
        'index': directives.unchanged,
        'date': directives.unchanged,
    }

    def run(self):
        """
        Builds the mathdef text.
        """
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
            return [quote]  # pragma: no cover

        # mid
        tag = self.options.get('tag', 'quotetag').strip()
        if len(tag) == 0:
            raise ValueError("tag is empty")  # pragma: no cover

        def __(text):
            if text:
                return _(text)
            return ""

        # book
        author = __(self.options.get('author', "").strip())
        book = __(self.options.get('book', "").strip())
        pages = __(self.options.get('pages', "").strip())
        year = __(self.options.get('year', "").strip())
        source = __(self.options.get('source', "").strip())
        index = __(self.options.get('index', "").strip())
        date = __(self.options.get('date', "").strip())

        indexes = []
        if index:
            indexes.append(index)  # pragma: no cover

        # add a label
        lid = self.options.get('lid', self.options.get('label', None))
        if lid:
            tnl = ['', ".. _{0}:".format(lid), ""]
        else:
            tnl = []  # pragma: no cover

        if author:
            tnl.append("**{0}**, ".format(author))
            indexes.append(author)
        if book:
            tnl.append("*{0}*".format(book))
            indexes.append(book)
        if pages:
            tnl.append(", {0}".format(pages))
        if date:
            tnl.append(" ({0})".format(date))
        if source:
            if source.startswith("http"):
                tnl.append(", `source <{0}>`_".format(source))
            else:
                tnl.append(", {0}".format(source))
        tnl.append('')
        tnl.append(".. index:: " + ", ".join(indexes))
        tnl.append('')

        content = StringList(tnl)
        content = content + self.content
        node = quote_node()

        try:
            nested_parse_with_titles(self.state, content, node)
        except Exception as e:  # pragma: no cover
            from sphinx.util import logging
            logger = logging.getLogger("blogpost")
            logger.warning(
                "[blogpost] unable to parse '{0}' - '{1}' - {2}".format(author, book, e))
            raise e

        node['tag'] = tag
        node['author'] = author
        node['pages'] = pages
        node['year'] = year
        node['label'] = lid
        node['source'] = source
        node['book'] = book
        node['index'] = index
        node['content'] = '\n'.join(self.content)
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


def visit_quote_node_rst(self, node):
    """
    visit_quote_node
    """
    self.new_state(0)
    self.add_text(".. quote::")
    for k, v in sorted(node.attributes.items()):
        if k in ("content", 'classes'):
            continue
        if v:
            self.new_state(4)
            self.add_text(":{0}: {1}".format(k, v))
            self.end_state(wrap=False, end=None)
    self.add_text(self.nl)
    self.new_state(4)
    self.add_text(node['content'])
    self.end_state()
    self.end_state()
    raise nodes.SkipNode


def depart_quote_node_rst(self, node):
    """
    depart_quote_node,
    see https://github.com/sphinx-doc/sphinx/blob/master/sphinx/writers/html.py
    """
    pass


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
                 rst=(visit_quote_node_rst, depart_quote_node_rst))

    app.add_directive('quote', QuoteNode)
    return {'version': sphinx.__display_version__, 'parallel_read_safe': True}
