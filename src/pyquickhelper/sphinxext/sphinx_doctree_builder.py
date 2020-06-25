# -*- coding: utf-8 -*-
"""
@file
@brief Defines a sphinx extension to output :epkg:`sphinx` doctree.

.. versionadded:: 1.8
"""
import os
import textwrap
from os import path
from sphinx.util import logging
from docutils.io import StringOutput
from sphinx.builders import Builder
from sphinx.util.osutil import ensuredir
from docutils import nodes, writers
from sphinx.writers.text import MAXWIDTH, STDINDENT
from ._sphinx_common_builder import CommonSphinxWriterHelpers


class DocTreeTranslator(nodes.NodeVisitor, CommonSphinxWriterHelpers):
    """
    Defines a translator for doctree
    """

    def __init__(self, builder, document):
        if not hasattr(builder, 'config'):
            raise TypeError(  # pragma: no cover
                "Unexpected type for builder {0}".format(type(builder)))
        nodes.NodeVisitor.__init__(self, document)
        self.builder = builder

        newlines = builder.config.text_newlines
        if newlines == 'windows':
            self.nl = '\r\n'
        elif newlines == 'native':
            self.nl = os.linesep
        else:
            self.nl = '\n'
        self.states = [[]]
        self.stateindent = [0]
        if self.builder.config.doctree_indent:
            self.indent = self.builder.config.doctree_indent
        else:
            self.indent = STDINDENT
        self.wrapper = textwrap.TextWrapper(
            width=STDINDENT, break_long_words=False, break_on_hyphens=False)
        self.dowrap = self.builder.config.doctree_wrap
        self.inline = self.builder.config.doctree_inline
        self._table = []

    def log_unknown(self, type, node):
        logger = logging.getLogger("DocTreeBuilder")
        logger.warning(
            "[doctree] %s(%s) unsupported formatting" % (type, node))

    def wrap(self, text, width=STDINDENT):
        self.wrapper.width = width
        return self.wrapper.wrap(text)

    def add_text(self, text, indent=-1):
        self.states[-1].append((indent, text))

    def new_state(self, indent=STDINDENT):
        self.states.append([])
        self.stateindent.append(indent)

    def end_state(self, wrap=False, end=None):
        content = self.states.pop()
        maxindent = sum(self.stateindent)
        indent = self.stateindent.pop()
        result = []
        toformat = []

        def do_format():
            if not toformat:
                return
            if wrap:
                res = self.wrap(''.join(toformat), width=MAXWIDTH - maxindent)
            else:
                res = ''.join(toformat).splitlines()
            if end:
                res += end
            result.append((indent, res))

        for itemindent, item in content:
            if itemindent == -1:
                toformat.append(item)
            else:
                do_format()
                result.append((indent + itemindent, item))
                toformat = []

        do_format()
        self.states[-1].extend(result)

    def visit_document(self, node):
        self.new_state(0)

    def depart_document(self, node):
        self.end_state()
        self.body = self.nl.join(line and (' ' * indent + line)
                                 for indent, lines in self.states[0]
                                 for line in lines)

    def visit_Text(self, node):
        text = node.astext()
        if self.inline:
            text = text.replace("\n", "\\n").replace(
                "\r", "").replace("\t", "\\t")
        self.add_text(text)

    def depart_Text(self, node):
        pass

    def _format_obj(self, obj):
        if isinstance(obj, str):
            return "'{0}'".format(obj.replace("'", "\\'"))
        elif isinstance(obj, nodes.Node):
            return "<node={0}[...]>".format(obj.__class__.__name__)
        else:
            return str(obj)

    def unknown_visit(self, node):
        self.new_state(0)
        self.add_text("<{0}".format(node.__class__.__name__))
        if hasattr(node, 'attributes') and node.attributes:
            res = ['{0}={1}'.format(k, self._format_obj(v))
                   for k, v in sorted(node.attributes.items())
                   if v not in (None, [], '')]
            if res:
                if self.inline:
                    self.add_text(" " + " ".join(res))
                else:
                    for kv in res:
                        self.new_state()
                        self.add_text("- " + kv)
                        self.add_text(self.nl)
                        self.end_state()
        self.add_text(">")
        self.new_state()

    def unknown_departure(self, node):
        self.end_state(wrap=self.dowrap)
        self.add_text("</{0}>".format(node.__class__.__name__))
        self.end_state()


class DocTreeBuilder(Builder):
    """
    Defines a doctree builder.
    """
    name = 'doctree'
    format = 'doctree'
    file_suffix = '.doctree.txt'
    link_suffix = None
    default_translator_class = DocTreeTranslator

    def __init__(self, *args, **kwargs):
        """
        Constructor, add a logger.
        """
        Builder.__init__(self, *args, **kwargs)
        self.logger = logging.getLogger("DocTreeBuilder")

    def init(self):
        """
        Load necessary templates and perform initialization.
        """
        if self.config.doctree_file_suffix is not None:
            self.file_suffix = self.config.doctree_file_suffix
        if self.config.doctree_link_suffix is not None:
            self.link_suffix = self.config.doctree_link_suffix
        if self.link_suffix is None:
            self.link_suffix = self.file_suffix

        # Function to convert the docname to a reST file name.
        def file_transform(docname):
            return docname + self.file_suffix

        # Function to convert the docname to a relative URI.
        def link_transform(docname):
            return docname + self.link_suffix

        if self.config.doctree_file_transform is not None:
            self.file_transform = self.config.doctree_file_transform
        else:
            self.file_transform = file_transform
        if self.config.doctree_link_transform is not None:
            self.link_transform = self.config.doctree_link_transform
        else:
            self.link_transform = link_transform

    def get_outdated_docs(self):
        """
        Return an iterable of input files that are outdated.
        This method is taken from ``TextBuilder.get_outdated_docs()``
        with minor changes to support ``(confval, doctree_file_transform))``.
        """
        for docname in self.env.found_docs:
            if docname not in self.env.all_docs:
                yield docname
                continue
            sourcename = path.join(self.env.srcdir, docname +
                                   self.file_suffix)
            targetname = path.join(self.outdir, self.file_transform(docname))

            try:
                targetmtime = path.getmtime(targetname)
            except Exception:
                targetmtime = 0
            try:
                srcmtime = path.getmtime(sourcename)
                if srcmtime > targetmtime:
                    yield docname
            except EnvironmentError:
                # source doesn't exist anymore
                pass

    def get_target_uri(self, docname, typ=None):
        return self.link_transform(docname)

    def prepare_writing(self, docnames):
        self.writer = DocTreeWriter(self)

    def get_outfilename(self, pagename):
        """
        Overwrites *get_target_uri* to control file names.
        """
        return "{0}/{1}.doctree.txt".format(self.outdir, pagename).replace("\\", "/")

    def write_doc(self, docname, doctree):
        destination = StringOutput(encoding='utf-8')
        self.current_docname = docname
        self.writer.write(doctree, destination)
        ctx = None
        self.handle_page(docname, ctx, event_arg=doctree)

    def handle_page(self, pagename, addctx, templatename=None,
                    outfilename=None, event_arg=None):
        if templatename is not None:
            raise NotImplementedError("templatename must be None.")
        outfilename = self.get_outfilename(pagename)
        ensuredir(path.dirname(outfilename))
        with open(outfilename, 'w', encoding='utf-8') as f:
            f.write(self.writer.output)

    def finish(self):
        pass


class DocTreeWriter(writers.Writer):
    """
    Defines a doctree writer.
    """
    supported = ('text',)
    settings_spec = ('No options here.', '', ())
    settings_defaults = {}
    translator_class = DocTreeTranslator

    output = None

    def __init__(self, builder):
        writers.Writer.__init__(self)
        self.builder = builder

    def translate(self):
        visitor = self.builder.create_translator(self.builder, self.document)
        self.document.walkabout(visitor)
        self.output = visitor.body


def setup(app):
    """
    Initializes the doctree builder.
    """
    app.add_builder(DocTreeBuilder)
    app.add_config_value('doctree_file_suffix', ".doctree.txt", 'env')
    app.add_config_value('doctree_link_suffix', None, 'env')
    app.add_config_value('doctree_file_transform', None, 'env')
    app.add_config_value('doctree_link_transform', None, 'env')
    app.add_config_value('doctree_indent', STDINDENT, 'env')
    app.add_config_value('doctree_image_dest', None, 'env')
    app.add_config_value('doctree_wrap', False, 'env')
    app.add_config_value('doctree_inline', True, 'env')
