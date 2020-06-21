"""
@file
@brief Helpers to convert docstring to various format.
"""
import os
import sys
from collections import deque
import warnings
import pickle
import platform
from html import escape as htmlescape
from io import StringIO
from docutils.parsers.rst import roles
from docutils.languages import en as docutils_en
from docutils import nodes
from docutils.utils import Reporter
from sphinx.application import Sphinx
from sphinx.environment import BuildEnvironment
from sphinx.errors import ExtensionError
from sphinx.ext.extlinks import setup_link_roles
from sphinx.transforms import SphinxTransformer
from sphinx.util.docutils import is_html5_writer_available
from sphinx.writers.html import HTMLWriter
from sphinx.util.build_phase import BuildPhase
from sphinx.util.logging import prefixed_warnings
from sphinx.project import Project
from sphinx.errors import ApplicationError
from sphinx.util.logging import getLogger
from ..sphinxext.sphinx_doctree_builder import DocTreeBuilder, DocTreeWriter, DocTreeTranslator
from ..sphinxext.sphinx_md_builder import MdBuilder, MdWriter, MdTranslator
from ..sphinxext.sphinx_latex_builder import EnhancedLaTeXBuilder, EnhancedLaTeXWriter, EnhancedLaTeXTranslator
from ..sphinxext.sphinx_rst_builder import RstBuilder, RstWriter, RstTranslator
from ._single_file_html_builder import CustomSingleFileHTMLBuilder


def _get_LaTeXTranslator():
    try:
        from sphinx.writers.latex import LaTeXTranslator
    except ImportError:  # pragma: no cover
        # Since sphinx 1.7.3 (circular reference).
        import sphinx.builders.latex.transforms
        from sphinx.writers.latex import LaTeXTranslator
    return LaTeXTranslator


if is_html5_writer_available():
    from sphinx.writers.html5 import HTML5Translator as HTMLTranslator
else:
    from sphinx.writers.html import HTMLTranslator  # pragma: no cover


def update_docutils_languages(values=None):
    """
    Updates ``docutils/languages/en.py`` with missing labels.
    It Does it for languages *en*.

    @param      values      consider values in this dictionaries first
    """
    if values is None:
        values = dict()
    lab = docutils_en.labels
    if 'versionmodified' not in lab:
        lab['versionmodified'] = values.get(
            'versionmodified', 'modified version')
    if 'desc' not in lab:
        lab['desc'] = values.get('desc', 'description')


class _AdditionalVisitDepart:
    """
    Additional visitors and departors.

    .. versionchanged:: 1.7
        Update for Sphinx 1.7.
    """

    def __init__(self, output_format):
        """
        .. versionadded:: 1.7
        """
        self.output_format = output_format

    def is_html(self):
        """
        Tells if the translator is :epkg:`html` format.
        """
        return self.base_class is HTMLTranslator

    def is_rst(self):
        """
        Tells if the translator is :epkg:`rst` format.
        """
        return self.base_class is RstTranslator

    def is_latex(self):
        """
        Tells if the translator is :epkg:`latex` format.
        """
        return self.base_class is _get_LaTeXTranslator()

    def is_md(self):
        """
        Tells if the translator is :epkg:`markdown` format.
        """
        return self.base_class is _get_LaTeXTranslator()

    def is_doctree(self):
        """
        Tells if the translator is doctree format.
        """
        return self.base_class is _get_LaTeXTranslator()

    def add_secnumber(self, node):
        """
        Overwrites this method to catch errors due when
        it is a single document being processed.
        """
        if node.get('secnumber'):
            self.base_class.add_secnumber(self, node)
        elif len(node.parent['ids']) > 0:
            self.base_class.add_secnumber(self, node)
        else:
            n = len(self.builder.secnumbers)
            node.parent['ids'].append("custom_label_%d" % n)
            self.base_class.add_secnumber(self, node)

    def eval_expr(self, expr):
        rst = self.output_format == 'rst'
        latex = self.output_format in ('latex', 'elatex')
        texinfo = [('index', 'A_AdditionalVisitDepart', 'B_AdditionalVisitDepart',   # pylint: disable=W0612
                    'C_AdditionalVisitDepart', 'D_AdditionalVisitDepart',
                    'E_AdditionalVisitDepart', 'Miscellaneous')]
        html = self.output_format == 'html'
        md = self.output_format == 'md'
        doctree = self.output_format in ('doctree', 'doctree.txt')
        if not(rst or html or latex or md or doctree):
            raise ValueError(  # pragma: no cover
                "Unknown output format '{0}'.".format(self.output_format))
        try:
            ev = eval(expr)
        except Exception:  # pragma: no cover
            raise ValueError(
                "Unable to interpret expression '{0}'".format(expr))
        return ev

    def visit_only(self, node):
        ev = self.eval_expr(node.attributes['expr'])
        if ev:
            pass
        else:
            raise nodes.SkipNode

    def depart_only(self, node):
        ev = self.eval_expr(node.attributes['expr'])
        if ev:
            pass
        else:
            # The program should not necessarily be here.
            pass

    def unknown_visit(self, node):  # pragma: no cover
        raise NotImplementedError("[_AdditionalVisitDepart] Unknown node: '{0}' in '{1}'".format(
            node.__class__.__name__, self.__class__.__name__))


class HTMLTranslatorWithCustomDirectives(_AdditionalVisitDepart, HTMLTranslator):
    """
    See @see cl HTMLWriterWithCustomDirectives.
    """

    def __init__(self, builder, *args, **kwds):
        """
        .. versionchanged:: 1.7
            Does something specific for :epkg:`HTML`. only is a node.
        """
        HTMLTranslator.__init__(self, builder, *args, **kwds)
        _AdditionalVisitDepart.__init__(self, 'html')
        nodes_list = getattr(builder, '_function_node', None)
        if nodes_list is not None:
            for name, f1, f2 in nodes_list:
                setattr(self.__class__, "visit_" + name, f1)
                setattr(self.__class__, "depart_" + name, f2)
        self.base_class = HTMLTranslator

    def visit_field(self, node):
        if not hasattr(self, '_fieldlist_row_index'):
            # needed when a docstring starts with :param:
            self._fieldlist_row_index = 0
        return HTMLTranslator.visit_field(self, node)

    def visit_pending_xref(self, node):
        self.visit_Text(node)
        raise nodes.SkipNode

    def unknown_visit(self, node):  # pragma: no cover
        raise NotImplementedError("[HTMLTranslatorWithCustomDirectives] Unknown node: '{0}' in '{1}'".format(
            node.__class__.__name__, self.__class__.__name__))


class RSTTranslatorWithCustomDirectives(_AdditionalVisitDepart, RstTranslator):
    """
    See @see cl HTMLWriterWithCustomDirectives.
    """

    def __init__(self, builder, *args, **kwds):
        """
        constructor
        """
        RstTranslator.__init__(self, builder, *args, **kwds)
        _AdditionalVisitDepart.__init__(self, 'rst')
        for name, f1, f2 in builder._function_node:
            setattr(self.__class__, "visit_" + name, f1)
            setattr(self.__class__, "depart_" + name, f2)
        self.base_class = RstTranslator


class MDTranslatorWithCustomDirectives(_AdditionalVisitDepart, MdTranslator):
    """
    See @see cl HTMLWriterWithCustomDirectives.
    """

    def __init__(self, builder, *args, **kwds):
        """
        constructor
        """
        MdTranslator.__init__(self, builder, *args, **kwds)
        _AdditionalVisitDepart.__init__(self, 'md')
        for name, f1, f2 in builder._function_node:
            setattr(self.__class__, "visit_" + name, f1)
            setattr(self.__class__, "depart_" + name, f2)
        self.base_class = MdTranslator


class DocTreeTranslatorWithCustomDirectives(DocTreeTranslator):
    """
    See @see cl HTMLWriterWithCustomDirectives.
    """

    def __init__(self, builder, *args, **kwds):
        """
        constructor
        """
        DocTreeTranslator.__init__(self, builder, *args, **kwds)
        self.base_class = DocTreeTranslator


class LatexTranslatorWithCustomDirectives(_AdditionalVisitDepart, EnhancedLaTeXTranslator):
    """
    See @see cl LatexWriterWithCustomDirectives.
    """

    def __init__(self, builder, document, *args, **kwds):
        """
        constructor
        """
        if not hasattr(builder, "config"):
            builder, document = document, builder
        if not hasattr(builder, "config"):
            raise TypeError(  # pragma: no cover
                "Builder has no config: {} - {}".format(type(builder), type(document)))
        EnhancedLaTeXTranslator.__init__(
            self, builder, document, *args, **kwds)
        _AdditionalVisitDepart.__init__(self, 'md')
        for name, f1, f2 in builder._function_node:
            setattr(self.__class__, "visit_" + name, f1)
            setattr(self.__class__, "depart_" + name, f2)
        self.base_class = EnhancedLaTeXTranslator


class _WriterWithCustomDirectives:
    """
    Common class to @see cl HTMLWriterWithCustomDirectives and @see cl RSTWriterWithCustomDirectives.
    """

    def _init(self, base_class, translator_class, app=None):
        """
        @param      base_class  base class
        @param      app         Sphinx application
        """
        if app is None:
            self.app = _CustomSphinx(srcdir=None, confdir=None, outdir=None, doctreedir=None,
                                     buildername='memoryhtml')
        else:
            self.app = app
        builder = self.app.builder
        builder.fignumbers = {}
        base_class.__init__(self, builder)
        self.translator_class = translator_class
        self.builder.secnumbers = {}
        self.builder._function_node = []
        self.builder.current_docname = None
        self.base_class = base_class

    def connect_directive_node(self, name, f_visit, f_depart):
        """
        Adds custom node to the translator.

        @param      name        name of the directive
        @param      f_visit     visit function
        @param      f_depart    depart function
        """
        if self.builder.format != "doctree":
            self.builder._function_node.append((name, f_visit, f_depart))

    def add_configuration_options(self, new_options):
        """
        Add new options.

        @param      new_options     new options
        """
        for k, v in new_options.items():
            self.builder.config.values[k] = v

    def write(self, document, destination):
        """
        Processes a document into its final form.
        Translates `document` (a Docutils document tree) into the Writer's
        native format, and write it out to its `destination` (a
        `docutils.io.Output` subclass object).

        Normally not overridden or extended in subclasses.
        """
        # trans = self.builder.create_translator(self.builder, document)
        # if not isinstance(trans, HTMLTranslatorWithCustomDirectives):
        #     raise TypeError("The translator is not of a known type but '{0}'".format(type(trans)))
        self.base_class.write(self, document, destination)


class HTMLWriterWithCustomDirectives(_WriterWithCustomDirectives, HTMLWriter):
    """
    This :epkg:`docutils` writer extends the HTML writer with
    custom directives implemented in this module,
    @see cl RunPythonDirective, @see cl BlogPostDirective.

    See `Write your own ReStructuredText-Writer <http://www.arnebrodowski.de/blog/write-your-own-restructuredtext-writer.html>`_.

    This class needs to tell :epkg:`docutils` to call the added function
    when directives *runpython* or *blogpost* are met.
    """

    def __init__(self, builder=None, app=None):  # pylint: disable=W0231
        """
        @param      builder builder
        @param      app     Sphinx application
        """
        _WriterWithCustomDirectives._init(
            self, HTMLWriter, HTMLTranslatorWithCustomDirectives, app)

    def translate(self):
        self.visitor = visitor = self.translator_class(
            self.builder, self.document)
        self.document.walkabout(visitor)
        self.output = visitor.astext()
        for attr in ('head_prefix', 'stylesheet', 'head', 'body_prefix',
                     'body_pre_docinfo', 'docinfo', 'body', 'fragment',
                     'body_suffix', 'meta', 'title', 'subtitle', 'header',
                     'footer', 'html_prolog', 'html_head', 'html_title',
                     'html_subtitle', 'html_body', ):
            setattr(self, attr, getattr(visitor, attr, None))
        self.clean_meta = ''.join(visitor.meta[2:])


class RSTWriterWithCustomDirectives(_WriterWithCustomDirectives, RstWriter):
    """
    This :epkg:`docutils` writer extends the :epkg:`RST` writer with
    custom directives implemented in this module.
    """

    def __init__(self, builder=None, app=None):  # pylint: disable=W0231
        """
        @param      builder builder
        @param      app     Sphinx application
        """
        _WriterWithCustomDirectives._init(
            self, RstWriter, RSTTranslatorWithCustomDirectives, app)

    def translate(self):
        visitor = self.translator_class(self.builder, self.document)
        self.document.walkabout(visitor)
        self.output = visitor.body


class MDWriterWithCustomDirectives(_WriterWithCustomDirectives, MdWriter):
    """
    This :epkg:`docutils` writer extends the :epkg:`MD` writer with
    custom directives implemented in this module.
    """

    def __init__(self, builder=None, app=None):  # pylint: disable=W0231
        """
        @param      builder builder
        @param      app     Sphinx application
        """
        _WriterWithCustomDirectives._init(
            self, MdWriter, MDTranslatorWithCustomDirectives, app)

    def translate(self):
        visitor = self.translator_class(self.builder, self.document)
        self.document.walkabout(visitor)
        self.output = visitor.body


class DocTreeWriterWithCustomDirectives(_WriterWithCustomDirectives, DocTreeWriter):
    """
    This :epkg:`docutils` writer creates a doctree writer with
    custom directives implemented in this module.
    """

    def __init__(self, builder=None, app=None):  # pylint: disable=W0231
        """
        @param      builder builder
        @param      app     Sphinx application
        """
        _WriterWithCustomDirectives._init(
            self, DocTreeWriter, DocTreeTranslatorWithCustomDirectives, app)

    def translate(self):
        visitor = self.translator_class(self.builder, self.document)
        self.document.walkabout(visitor)
        self.output = visitor.body


class LatexWriterWithCustomDirectives(_WriterWithCustomDirectives, EnhancedLaTeXWriter):
    """
    This :epkg:`docutils` writer extends the :epkg:`Latex` writer with
    custom directives implemented in this module.
    """

    def __init__(self, builder=None, app=None):  # pylint: disable=W0231
        """
        @param      builder builder
        @param      app     Sphinx application
        """
        _WriterWithCustomDirectives._init(
            self, EnhancedLaTeXWriter, LatexTranslatorWithCustomDirectives, app)
        if not hasattr(self.builder, "config"):
            raise TypeError(  # pragma: no cover
                "Builder has no config: {}".format(type(self.builder)))

    def translate(self):
        if not hasattr(self.builder, "config"):
            raise TypeError(  # pragma: no cover
                "Builder has no config: {}".format(type(self.builder)))
        # The instruction
        # visitor = self.builder.create_translator(self.builder, self.document)
        # automatically adds methods visit_ and depart_ for translator
        # based on the list of registered extensions. Might be worth using it.
        visitor = self.translator_class(self.builder, self.document)
        self.document.walkabout(visitor)
        self.output = visitor.body


class _MemoryBuilder:
    """
    Builds :epkg:`HTML` output in memory.
    The API is defined by the page
    :epkg:`builderapi`.
    """

    def _init(self, base_class, app):
        """
        Constructs the builder.
        Most of the parameter are static members of the class and cannot
        be overwritten (yet).

        :param base_class: base builder class
        :param app: :epkg:`Sphinx application`
        """
        if "IMPOSSIBLE:TOFIND" in app.srcdir:
            import sphinx.util.osutil
            from .conf_path_tools import custom_ensuredir
            sphinx.util.osutil.ensuredir = custom_ensuredir
            sphinx.builders.ensuredir = custom_ensuredir

        base_class.__init__(self, app=app)
        self.built_pages = {}
        self.base_class = base_class

    def iter_pages(self):
        """
        Enumerate created pages.

        @return     iterator on tuple(name, content)
        """
        for k, v in self.built_pages.items():
            yield k, v.getvalue()

    def create_translator(self, *args):
        """
        Returns an instance of translator.
        This method returns an instance of ``default_translator_class`` by default.
        Users can replace the translator class with ``app.set_translator()`` API.
        """
        translator_class = self.translator_class
        return translator_class(*args)

    def _write_serial(self, docnames):
        """
        Overwrites *_write_serial* to avoid writing on disk.
        """
        from sphinx.util.logging import pending_warnings
        from sphinx.util import status_iterator
        with pending_warnings():
            for docname in status_iterator(docnames, 'writing output... ', "darkgreen",
                                           len(docnames), self.app.verbosity):
                doctree = self.env.get_and_resolve_doctree(docname, self)
                self.write_doc_serialized(docname, doctree)
                self.write_doc(docname, doctree)

    def _write_parallel(self, docnames, nproc):
        """
        Not supported.
        """
        raise NotImplementedError(
            "Use parallel=0 when creating the sphinx application.")

    def assemble_doctree(self, *args, **kwargs):
        """
        Overwrites *assemble_doctree* to control the doctree.
        """
        from sphinx.util.nodes import inline_all_toctrees
        from sphinx.util.console import darkgreen
        master = self.config.master_doc
        if hasattr(self, "doctree_"):
            tree = self.doctree_
        else:
            raise AttributeError(
                "Attribute 'doctree_' is not present. Call method finalize().")
        tree = inline_all_toctrees(
            self, set(), master, tree, darkgreen, [master])
        tree['docname'] = master
        self.env.resolve_references(tree, master, self)
        self.fix_refuris(tree)
        return tree

    def fix_refuris(self, tree):
        """
        Overwrites *fix_refuris* to control the reference names.
        """
        fname = "__" + self.config.master_doc + "__"
        for refnode in tree.traverse(nodes.reference):
            if 'refuri' not in refnode:
                continue
            refuri = refnode['refuri']
            hashindex = refuri.find('#')
            if hashindex < 0:
                continue
            hashindex = refuri.find('#', hashindex + 1)
            if hashindex >= 0:
                refnode['refuri'] = fname + refuri[hashindex:]

    def get_target_uri(self, docname, typ=None):
        """
        Overwrites *get_target_uri* to control the page name.
        """
        if docname in self.env.all_docs:
            # all references are on the same page...
            return self.config.master_doc + '#document-' + docname
        elif docname in ("genindex", "search"):
            return self.config.master_doc + '-#' + docname
        else:
            docs = ", ".join(sorted("'{0}'".format(_)
                                    for _ in self.env.all_docs))
            raise ValueError(
                "docname='{0}' should be in 'self.env.all_docs' which contains:\n{1}".format(docname, docs))

    def get_outfilename(self, pagename):
        """
        Overwrites *get_target_uri* to control file names.
        """
        return "{0}/{1}.m.html".format(self.outdir, pagename).replace("\\", "/")

    def handle_page(self, pagename, addctx, templatename='page.html',
                    outfilename=None, event_arg=None):
        """
        Overrides *handle_page* to write into stream instead of files.
        """
        from sphinx.util.osutil import relative_uri
        ctx = self.globalcontext.copy()
        if hasattr(self, "warning"):
            ctx['warn'] = self.warning
        elif hasattr(self, "warn"):
            ctx['warn'] = self.warn
        # current_page_name is backwards compatibility
        ctx['pagename'] = ctx['current_page_name'] = pagename
        ctx['encoding'] = self.config.html_output_encoding
        default_baseuri = self.get_target_uri(pagename)
        # in the singlehtml builder, default_baseuri still contains an #anchor
        # part, which relative_uri doesn't really like...
        default_baseuri = default_baseuri.rsplit('#', 1)[0]

        def pathto(otheruri, resource=False, baseuri=default_baseuri):
            if resource and '://' in otheruri:
                # allow non-local resources given by scheme
                return otheruri
            elif not resource:
                otheruri = self.get_target_uri(otheruri)
            uri = relative_uri(baseuri, otheruri) or '#'
            if uri == '#' and not self.allow_sharp_as_current_path:
                uri = baseuri
            return uri
        ctx['pathto'] = pathto

        def css_tag(css):
            attrs = []
            for key in sorted(css.attributes):
                value = css.attributes[key]
                if value is not None:
                    attrs.append('%s="%s"' % (key, htmlescape(    # pylint: disable=W1505
                        value, True)))  # pylint: disable=W1505
            attrs.append('href="%s"' % pathto(css.filename, resource=True))
            return '<link %s />' % ' '.join(attrs)
        ctx['css_tag'] = css_tag

        def hasdoc(name):
            if name in self.env.all_docs:
                return True
            elif name == 'search' and self.search:
                return True
            elif name == 'genindex' and self.get_builder_config('use_index', 'html'):
                return True
            return False
        ctx['hasdoc'] = hasdoc

        ctx['toctree'] = lambda **kw: self._get_local_toctree(pagename, **kw)
        self.add_sidebars(pagename, ctx)
        ctx.update(addctx)

        self.update_page_context(pagename, templatename, ctx, event_arg)
        newtmpl = self.app.emit_firstresult('html-page-context', pagename,
                                            templatename, ctx, event_arg)
        if newtmpl:
            templatename = newtmpl

        try:
            output = self.templates.render(templatename, ctx)
        except UnicodeError:  # pragma: no cover
            logger = getLogger("MockSphinxApp")
            logger.warning("[_CustomSphinx] A unicode error occurred when rendering the page %s. "
                           "Please make sure all config values that contain "
                           "non-ASCII content are Unicode strings.", pagename)
            return

        if not outfilename:
            outfilename = self.get_outfilename(pagename)
        # outfilename's path is in general different from self.outdir
        # ensuredir(path.dirname(outfilename))
        if outfilename not in self.built_pages:
            self.built_pages[outfilename] = StringIO()
        self.built_pages[outfilename].write(output)


class MemoryHTMLBuilder(_MemoryBuilder, CustomSingleFileHTMLBuilder):
    """
    Builds :epkg:`HTML` output in memory.
    The API is defined by the page
    :epkg:`builderapi`.
    """
    name = 'memoryhtml'
    format = 'html'
    out_suffix = None  # ".memory.html"
    supported_image_types = ['application/pdf', 'image/png', 'image/jpeg']
    default_translator_class = HTMLTranslatorWithCustomDirectives
    translator_class = HTMLTranslatorWithCustomDirectives
    _writer_class = HTMLWriterWithCustomDirectives
    supported_remote_images = True
    supported_data_uri_images = True
    html_scaled_image_link = True

    def __init__(self, app):  # pylint: disable=W0231
        """
        Construct the builder.
        Most of the parameter are static members of the class and cannot
        be overwritten (yet).

        :param app: :epkg:`Sphinx application`
        """
        _MemoryBuilder._init(self, CustomSingleFileHTMLBuilder, app)


class MemoryRSTBuilder(_MemoryBuilder, RstBuilder):

    """
    Builds :epkg:`RST` output in memory.
    The API is defined by the page
    :epkg:`builderapi`.
    The writer simplifies the :epkg:`RST` syntax by replacing
    custom roles into true :epkg:`RST` syntax.
    """

    name = 'memoryrst'
    format = 'rst'
    out_suffix = None  # ".memory.rst"
    supported_image_types = ['application/pdf', 'image/png', 'image/jpeg']
    default_translator_class = RSTTranslatorWithCustomDirectives
    translator_class = RSTTranslatorWithCustomDirectives
    _writer_class = RSTWriterWithCustomDirectives
    supported_remote_images = True
    supported_data_uri_images = True
    html_scaled_image_link = True

    def __init__(self, app):  # pylint: disable=W0231
        """
        Construct the builder.
        Most of the parameter are static members of the class and cannot
        be overwritten (yet).

        :param app: :epkg:`Sphinx application`
        """
        _MemoryBuilder._init(self, RstBuilder, app)

    def handle_page(self, pagename, addctx, templatename=None,
                    outfilename=None, event_arg=None):
        """
        Override *handle_page* to write into stream instead of files.
        """
        if templatename is not None:
            raise NotImplementedError(
                "templatename must be None.")  # pragma: no cover
        if not outfilename:
            outfilename = self.get_outfilename(pagename)
        if outfilename not in self.built_pages:
            self.built_pages[outfilename] = StringIO()
        self.built_pages[outfilename].write(self.writer.output)


class MemoryMDBuilder(_MemoryBuilder, MdBuilder):
    """
    Builds :epkg:`MD` output in memory.
    The API is defined by the page
    :epkg:`builderapi`.
    """
    name = 'memorymd'
    format = 'md'
    out_suffix = None  # ".memory.rst"
    supported_image_types = ['application/pdf', 'image/png', 'image/jpeg']
    default_translator_class = MDTranslatorWithCustomDirectives
    translator_class = MDTranslatorWithCustomDirectives
    _writer_class = MDWriterWithCustomDirectives
    supported_remote_images = True
    supported_data_uri_images = True
    html_scaled_image_link = True

    def __init__(self, app):  # pylint: disable=W0231
        """
        Construct the builder.
        Most of the parameter are static members of the class and cannot
        be overwritten (yet).

        :param app: :epkg:`Sphinx application`
        """
        _MemoryBuilder._init(self, MdBuilder, app)

    def handle_page(self, pagename, addctx, templatename=None,
                    outfilename=None, event_arg=None):
        """
        Override *handle_page* to write into stream instead of files.
        """
        if templatename is not None:
            raise NotImplementedError(
                "templatename must be None.")  # pragma: no cover
        if not outfilename:
            outfilename = self.get_outfilename(pagename)
        if outfilename not in self.built_pages:
            self.built_pages[outfilename] = StringIO()
        self.built_pages[outfilename].write(self.writer.output)


class MemoryDocTreeBuilder(_MemoryBuilder, DocTreeBuilder):
    """
    Builds doctree output in memory.
    The API is defined by the page
    :epkg:`builderapi`.
    """
    name = 'memorydoctree'
    format = 'doctree'
    out_suffix = None  # ".memory.rst"
    default_translator_class = DocTreeTranslatorWithCustomDirectives
    translator_class = DocTreeTranslatorWithCustomDirectives
    _writer_class = DocTreeWriterWithCustomDirectives
    supported_remote_images = True
    supported_data_uri_images = True
    html_scaled_image_link = True

    def __init__(self, app):  # pylint: disable=W0231
        """
        Constructs the builder.
        Most of the parameter are static members of the class and cannot
        be overwritten (yet).

        :param app: :epkg:`Sphinx application`
        """
        _MemoryBuilder._init(self, DocTreeBuilder, app)

    def handle_page(self, pagename, addctx, templatename=None,
                    outfilename=None, event_arg=None):
        """
        Override *handle_page* to write into stream instead of files.
        """
        if templatename is not None:
            raise NotImplementedError(
                "templatename must be None.")  # pragma: no cover
        if not outfilename:
            outfilename = self.get_outfilename(pagename)
        if outfilename not in self.built_pages:
            self.built_pages[outfilename] = StringIO()
        self.built_pages[outfilename].write(self.writer.output)


class MemoryLatexBuilder(_MemoryBuilder, EnhancedLaTeXBuilder):
    """
    Builds :epkg:`Latex` output in memory.
    The API is defined by the page
    :epkg:`builderapi`.
    """
    name = 'memorylatex'
    format = 'tex'
    out_suffix = None  # ".memory.tex"
    supported_image_types = ['image/png', 'image/jpeg', 'image/gif']
    default_translator_class = LatexTranslatorWithCustomDirectives
    translator_class = LatexTranslatorWithCustomDirectives
    _writer_class = LatexWriterWithCustomDirectives
    supported_remote_images = True
    supported_data_uri_images = True
    html_scaled_image_link = True

    def __init__(self, app):  # pylint: disable=W0231
        """
        Constructs the builder.
        Most of the parameter are static members of the class and cannot
        be overwritten (yet).

        :param app: :epkg:`Sphinx application`
        """
        _MemoryBuilder._init(self, EnhancedLaTeXBuilder, app)

    def write_stylesheet(self):
        from sphinx.highlighting import PygmentsBridge
        highlighter = PygmentsBridge('latex', self.config.pygments_style)
        rows = []
        rows.append('\\NeedsTeXFormat{LaTeX2e}[1995/12/01]\n')
        rows.append('\\ProvidesPackage{sphinxhighlight}')
        rows.append(
            '[2016/05/29 stylesheet for highlighting with pygments]\n\n')
        rows.append(highlighter.get_stylesheet())
        self.built_pages['sphinxhighlight.sty'] = StringIO()
        self.built_pages['sphinxhighlight.sty'].write("".join(rows))

    class EnhancedStringIO(StringIO):
        def write(self, content):
            if isinstance(content, str):
                StringIO.write(self, content)
            else:
                for line in content:
                    StringIO.write(self, line)

    def _get_filename(self, targetname, encoding='utf-8', overwrite_if_changed=True):
        if not isinstance(targetname, str):
            raise TypeError(  # pragma: no cover
                "targetname must be a string: {0}".format(targetname))
        destination = MemoryLatexBuilder.EnhancedStringIO()
        self.built_pages[targetname] = destination
        return destination


class _CustomBuildEnvironment(BuildEnvironment):
    """
    Overrides some functionalities of
    `BuildEnvironment <http://www.sphinx-doc.org/en/stable/extdev/envapi.html>`_.
    """

    def __init__(self, app):
        """
        """
        BuildEnvironment.__init__(self, app)
        self.doctree_ = {}

    def get_doctree(self, docname):
        """Read the doctree for a file from the pickle and return it."""
        if hasattr(self, "doctree_") and docname in self.doctree_:
            from sphinx.util.docutils import WarningStream
            doctree = self.doctree_[docname]
            doctree.settings.env = self
            doctree.reporter = Reporter(self.doc2path(
                docname), 2, 5, stream=WarningStream())
            return doctree

        if hasattr(self, "doctree_"):
            available = list(sorted(self.doctree_))
            if len(available) > 10:
                available = available[10:]
            raise KeyError(
                "Unable to find entry '{}' (has doctree: {})\nFirst documents:\n{}"
                "".format(
                    docname, hasattr(self, "doctree_"),
                    "\n".join(available)))

        raise KeyError(  # pragma: no cover
            "Doctree empty or not found for '{}' (has doctree: {})"
            "".format(
                docname, hasattr(self, "doctree_")))
        # return BuildEnvironment.get_doctree(self, docname)

    def apply_post_transforms(self, doctree, docname):
        """Apply all post-transforms."""
        # set env.docname during applying post-transforms
        self.temp_data['docname'] = docname

        transformer = SphinxTransformer(doctree)
        transformer.set_environment(self)
        transformer.add_transforms(self.app.post_transforms)
        transformer.apply_transforms()
        self.temp_data.clear()


class _CustomSphinx(Sphinx):
    """
    Custom :epkg:`Sphinx` application to avoid using disk.
    """

    def __init__(self, srcdir, confdir, outdir, doctreedir, buildername="memoryhtml",  # pylint: disable=W0231
                 confoverrides=None, status=None, warning=None,
                 freshenv=False, warningiserror=False,
                 tags=None, verbosity=0, parallel=0, keep_going=False,
                 new_extensions=None):
        '''
        Same constructor as :epkg:`Sphinx application`.
        Additional parameters:

        @param      new_extensions      extensions to add to the application

        Some insights about domains:

        ::

            {'cpp': sphinx.domains.cpp.CPPDomain,
             'js': sphinx.domains.javascript.JavaScriptDomain,
             'std': sphinx.domains.std.StandardDomain,
             'py': sphinx.domains.python.PythonDomain,
             'rst': sphinx.domains.rst.ReSTDomain,
             'c': sphinx.domains.c.CDomain}

        And builders:

        ::

            {'epub': ('epub', 'EpubBuilder'),
            'singlehtml': ('html', 'SingleFileHTMLBuilder'),
            'qthelp': ('qthelp', 'QtHelpBuilder'),
            'epub3': ('epub3', 'Epub3Builder'),
            'man': ('manpage', 'ManualPageBuilder'),
            'dummy': ('dummy', 'DummyBuilder'),
            'json': ('html', 'JSONHTMLBuilder'),
            'html': ('html', 'StandaloneHTMLBuilder'),
            'xml': ('xml', 'XMLBuilder'),
            'texinfo': ('texinfo', 'TexinfoBuilder'),
            'devhelp': ('devhelp', 'DevhelpBuilder'),
            'web': ('html', 'PickleHTMLBuilder'),
            'pickle': ('html', 'PickleHTMLBuilder'),
            'htmlhelp': ('htmlhelp', 'HTMLHelpBuilder'),
            'applehelp': ('applehelp', 'AppleHelpBuilder'),
            'linkcheck': ('linkcheck', 'CheckExternalLinksBuilder'),
            'dirhtml': ('html', 'DirectoryHTMLBuilder'),
            'latex': ('latex', 'LaTeXBuilder'),
            'elatex': ('latex', 'EnchancedLaTeXBuilder'),
            'text': ('text', 'TextBuilder'),
            'changes': ('changes', 'ChangesBuilder'),
            'websupport': ('websupport', 'WebSupportBuilder'),
            'gettext': ('gettext', 'MessageCatalogBuilder'),
            'pseudoxml': ('xml', 'PseudoXMLBuilder')}
            'rst': ('rst', 'RstBuilder')}
            'md': ('md', 'MdBuilder'),
            'doctree': ('doctree', 'DocTreeBuilder')}
        '''
        # own purpose (to monitor)
        self._logger = getLogger("_CustomSphinx")
        self._added_objects = []
        self._added_collectors = []

        # from sphinx.domains.cpp import CPPDomain
        # from sphinx.domains.javascript import JavaScriptDomain
        # from sphinx.domains.python import PythonDomain
        # from sphinx.domains.std import StandardDomain
        # from sphinx.domains.rst import ReSTDomain
        # from sphinx.domains.c import CDomain

        from sphinx.registry import SphinxComponentRegistry
        self.phase = BuildPhase.INITIALIZATION
        self.verbosity = verbosity
        self.extensions = {}
        self.builder = None
        self.env = None
        self.project = None
        self.registry = SphinxComponentRegistry()
        self.post_transforms = []
        self.html_themes = {}

        if doctreedir is None:
            doctreedir = "IMPOSSIBLE:TOFIND"
        if srcdir is None:
            srcdir = "IMPOSSIBLE:TOFIND"
        update_docutils_languages()

        self.srcdir = os.path.abspath(srcdir)
        self.confdir = os.path.abspath(
            confdir) if confdir is not None else None
        self.outdir = os.path.abspath(outdir) if confdir is not None else None
        self.doctreedir = os.path.abspath(doctreedir)
        self.parallel = parallel

        if self.srcdir == self.outdir:
            raise ApplicationError('Source directory and destination '  # pragma: no cover
                                   'directory cannot be identical')

        if status is None:
            self._status = StringIO()
            self.quiet = True
        else:
            self._status = status
            self.quiet = False

        from sphinx.events import EventManager
        # logging.setup(self, self._status, self._warning)
        self.events = EventManager(self)

        # keep last few messages for traceback
        # This will be filled by sphinx.util.logging.LastMessagesWriter
        self.messagelog = deque(maxlen=10)

        # say hello to the world
        from sphinx import __display_version__
        self.info('Running Sphinx v%s' %
                  __display_version__)  # pragma: no cover

        # notice for parallel build on macOS and py38+
        if sys.version_info > (3, 8) and platform.system() == 'Darwin' and parallel > 1:
            self._logger.info(  # pragma: no cover
                "For security reason, parallel mode is disabled on macOS and "
                "python3.8 and above.  For more details, please read "
                "https://github.com/sphinx-doc/sphinx/issues/6803")

        # status code for command-line application
        self.statuscode = 0

        # delayed import to speed up time
        from sphinx.application import builtin_extensions
        try:
            from sphinx.application import CONFIG_FILENAME, Config, Tags
            sphinx_version = 2  # pragma: no cover
        except ImportError:
            # Sphinx 3.0.0
            from sphinx.config import CONFIG_FILENAME, Config, Tags
            sphinx_version = 3

        # read config
        self.tags = Tags(tags)
        with warnings.catch_warnings():
            warnings.simplefilter(
                "ignore", (DeprecationWarning, PendingDeprecationWarning))
            if self.confdir is None:
                self.config = Config({}, confoverrides or {})
            else:  # pragma: no cover
                try:
                    self.config = Config.read(
                        self.confdir, confoverrides or {}, self.tags)
                except AttributeError:
                    try:
                        self.config = Config(  # pylint: disable=E1121
                            confdir, confoverrides or {}, self.tags)
                    except TypeError:
                        try:
                            self.config = Config(confdir, CONFIG_FILENAME,  # pylint: disable=E1121
                                                 confoverrides or {}, self.tags)
                        except TypeError:
                            # Sphinx==3.0.0
                            self.config = Config({}, confoverrides or {})
        self.sphinx__display_version__ = __display_version__

        # create the environment
        if sphinx_version == 2:  # pragma: no cover
            with warnings.catch_warnings():
                warnings.simplefilter(
                    "ignore", (DeprecationWarning, PendingDeprecationWarning, ImportWarning))
                self.config.check_unicode()
        self.config.pre_init_values()

        # set up translation infrastructure
        self._init_i18n()

        # check the Sphinx version if requested
        if (self.config.needs_sphinx and self.config.needs_sphinx >
                __display_version__):  # pragma: no cover
            from sphinx.locale import _
            from sphinx.application import VersionRequirementError
            raise VersionRequirementError(
                _('This project needs at least Sphinx v%s and therefore cannot '
                  'be built with this version.') % self.config.needs_sphinx)

        # set confdir to srcdir if -C given (!= no confdir); a few pieces
        # of code expect a confdir to be set
        if self.confdir is None:
            self.confdir = self.srcdir

        # load all built-in extension modules
        for extension in builtin_extensions:
            try:
                with warnings.catch_warnings():
                    warnings.filterwarnings(
                        "ignore", category=DeprecationWarning)
                    self.setup_extension(extension)
            except Exception as e:  # pragma: no cover
                if 'sphinx.builders.applehelp' not in str(e):  # pragma: no cover
                    mes = "Unable to run setup_extension '{0}'\nWHOLE LIST\n{1}".format(
                        extension, "\n".join(builtin_extensions))
                    raise ExtensionError(mes) from e

        # load all user-given extension modules
        for extension in self.config.extensions:
            self.setup_extension(extension)

        # /1 addition to the original code
        # additional extensions
        if new_extensions:
            for extension in new_extensions:
                if isinstance(extension, str):
                    self.setup_extension(extension)
                else:
                    # We assume it is a module.
                    dirname = os.path.dirname(extension.__file__)
                    sys.path.insert(0, dirname)
                    self.setup_extension(extension.__name__)
                    del sys.path[0]

        # add default HTML builders
        self.add_builder(MemoryHTMLBuilder)
        self.add_builder(MemoryRSTBuilder)
        self.add_builder(MemoryMDBuilder)
        self.add_builder(MemoryLatexBuilder)
        self.add_builder(MemoryDocTreeBuilder)

        if isinstance(buildername, tuple):
            if len(buildername) != 2:
                raise ValueError(
                    "The builder can be custom but it must be specifed as a 2-uple=(builder_name, builder_class).")
            self.add_builder(buildername[1])
            buildername = buildername[0]

        # /1 end of addition

        # preload builder module (before init config values)
        self.preload_builder(buildername)

        # the config file itself can be an extension
        if self.config.setup:
            prefix = 'while setting up extension %s:' % "conf.py"
            if prefixed_warnings is not None:
                with prefixed_warnings(prefix):
                    if callable(self.config.setup):
                        self.config.setup(self)
                    else:  # pragma: no cover
                        from sphinx.locale import _
                        from sphinx.application import ConfigError
                        raise ConfigError(
                            _("'setup' as currently defined in conf.py isn't a Python callable. "
                              "Please modify its definition to make it a callable function. This is "
                              "needed for conf.py to behave as a Sphinx extension.")
                        )
            elif callable(self.config.setup):
                self.config.setup(self)

        # now that we know all config values, collect them from conf.py
        noallowed = []
        rem = []
        for k in confoverrides:
            if k in {'initial_header_level', 'doctitle_xform', 'input_encoding',
                     'outdir', 'warnings_log', 'extensions'}:
                continue
            if k == 'override_image_directive':
                self.config.images_config["override_image_directive"] = True
                rem.append(k)
                continue
            if k not in self.config.values:
                noallowed.append(k)
        for k in rem:
            del confoverrides[k]
        if len(noallowed) > 0:
            raise ValueError(
                "The following configuration values are declared in any extension.\n--???--\n"
                "{0}\n--DECLARED--\n{1}".format(
                    "\n".join(sorted(noallowed)),
                    "\n".join(sorted(self.config.values))))

        # now that we know all config values, collect them from conf.py
        self.config.init_values()
        self.events.emit('config-inited', self.config)

        # /2 addition to the original code
        # check extension versions if requested
        # self.config.needs_extensions = self.config.extensions
        if not hasattr(self.config, 'items'):

            def _citems():
                for k, v in self.config.values.items():
                    yield k, v

            self.config.items = _citems

        # /2 end of addition

        # create the project
        self.project = Project(self.srcdir, self.config.source_suffix)
        # create the builder
        self.builder = self.create_builder(buildername)
        # set up the build environment
        self._init_env(freshenv)
        # set up the builder
        self._init_builder()

        if not isinstance(self.env, _CustomBuildEnvironment):
            raise TypeError(  # pragma: no cover
                "self.env is not _CustomBuildEnvironment: '{0}' buildername='{1}'".format(type(self.env), buildername))

        # addition
        self._extended_init_()

    def _init_env(self, freshenv):
        if freshenv:
            self.env = _CustomBuildEnvironment(self)
            self.env.setup(self)
            if self.srcdir is not None and self.srcdir != "IMPOSSIBLE:TOFIND":
                self.env.find_files(self.config, self.builder)
        elif "IMPOSSIBLE:TOFIND" not in self.doctreedir:  # pragma: no cover
            from sphinx.application import ENV_PICKLE_FILENAME
            filename = os.path.join(self.doctreedir, ENV_PICKLE_FILENAME)
            try:
                self.info('loading pickled environment... ', nonl=True)
                with open(filename, 'rb') as f:
                    self.env = pickle.load(f)
                    self.env.setup(self)
                self.info('done')
            except Exception as err:
                self.info('failed: %s' % err)
                self._init_env(freshenv=True)
        elif self.env is None:
            self.env = _CustomBuildEnvironment(self)
            if hasattr(self.env, 'setup'):
                self.env.setup(self)
        if not hasattr(self.env, 'project') or self.env.project is None:
            raise AttributeError(  # pragma: no cover
                "self.env.project is not initialized.")

    def create_builder(self, name):
        """
        Creates a builder, raises an exception if name is None.
        """
        if name is None:
            raise ValueError(  # pragma: no cover
                "Builder name cannot be None")

        return self.registry.create_builder(self, name)

    def _extended_init_(self):
        """
        Additional initialization steps.
        """
        if not hasattr(self, "domains"):
            self.domains = {}
        if not hasattr(self, "_events"):
            self._events = {}

        # Otherwise, role issue is missing.
        setup_link_roles(self)

    def _lookup_doctree(self, doctree, node_type):
        for node in doctree.traverse(node_type):
            yield node

    def _add_missing_ids(self, doctree):
        for i, node in enumerate(self._lookup_doctree(doctree, None)):
            stype = str(type(node))
            if ('section' not in stype and 'title' not in stype and
                    'reference' not in stype):
                continue
            try:
                node['ids'][0]
            except IndexError:
                node['ids'] = ['missing%d' % i]
            except TypeError:  # pragma: no cover
                pass

    def finalize(self, doctree, external_docnames=None):
        """
        Finalizes the documentation after it was parsed.

        @param      doctree             doctree (or pub.document), available after publication
        @param      external_docnames   other docnames the doctree references
        """
        imgs = list(self._lookup_doctree(doctree, nodes.image))
        for img in imgs:
            img['save_uri'] = img['uri']

        if not isinstance(self.env, _CustomBuildEnvironment):
            raise TypeError(  # pragma: no cover
                "self.env is not _CustomBuildEnvironment: '{0}'".format(type(self.env)))
        if not isinstance(self.builder.env, _CustomBuildEnvironment):
            raise TypeError(  # pragma: no cover
                "self.builder.env is not _CustomBuildEnvironment: '{0}'".format(
                    type(self.builder.env)))
        self.doctree_ = doctree
        self.builder.doctree_ = doctree
        self.env.doctree_[self.config.master_doc] = doctree
        self.env.all_docs = {self.config.master_doc: self.config.master_doc}

        if external_docnames:
            for doc in external_docnames:
                self.env.all_docs[doc] = doc

        # This steps goes through many function including one
        # modifying paths in image node.
        # Look for node['candidates'] = candidates in Sphinx code.
        # If a path startswith('/'), it is removed.
        from sphinx.environment.collectors.asset import logger as logger_asset
        logger_asset.setLevel(40)  # only errors
        self._add_missing_ids(doctree)
        self.events.emit('doctree-read', doctree)
        logger_asset.setLevel(30)  # back to warnings

        for img in imgs:
            img['uri'] = img['save_uri']

        self.events.emit('doctree-resolved', doctree,
                         self.config.master_doc)
        self.builder.write(None, None, 'all')

    def debug(self, message, *args, **kwargs):
        self._logger.debug(message, *args, **kwargs)

    def info(self, message='', nonl=False):
        self._logger.info(message, nonl=nonl)

    def warning(self, message='', nonl=False, name=None, type=None, subtype=None):
        if "is already registered" not in message:
            self._logger.warning(
                "[_CustomSphinx] {0} -- {1}".format(message, name), nonl=nonl, type=type, subtype=subtype)

    def add_builder(self, builder, override=False):
        self._added_objects.append(('builder', builder))
        if builder.name not in self.registry.builders:
            self.debug('[_CustomSphinx]  adding builder: %r', builder)
            try:
                # Sphinx >= 1.8
                self.registry.add_builder(builder, override=override)
            except TypeError:  # pragma: no cover
                # Sphinx < 1.8
                self.registry.add_builder(builder)
        else:
            self.debug('[_CustomSphinx]  already added builder: %r', builder)

    def setup_extension(self, extname):
        self._added_objects.append(('extension', extname))

        logger = getLogger('sphinx.application')
        disa = logger.logger.disabled
        logger.logger.disabled = True

        # delayed import to speed up time
        try:
            with warnings.catch_warnings():
                warnings.filterwarnings(
                    "ignore", category=DeprecationWarning)
                self.registry.load_extension(self, extname)
        except Exception as e:
            raise ExtensionError(
                "Unable to setup extension '{0}'".format(extname)) from e
        finally:
            logger.logger = disa

    def add_directive(self, name, obj, content=None, arguments=None,  # pylint: disable=W0221
                      override=True, **options):
        self._added_objects.append(('directive', name))
        if name == 'plot' and obj.__name__ == 'PlotDirective':

            old_run = obj.run

            def run(self):
                """Run the plot directive."""
                logger = getLogger("MockSphinxApp")
                logger.info(
                    '[MockSphinxApp] PlotDirective: {}'.format(self.content))
                try:
                    res = old_run(self)
                    logger.info(
                        '[MockSphinxApp] PlotDirective ok')
                    return res
                except OSError as e:  # pragma: no cover
                    logger = getLogger("MockSphinxApp")
                    logger.info(
                        '[MockSphinxApp] PlotDirective failed: {}'.format(e))
                return []

            obj.run = run

        try:
            # Sphinx >= 1.8
            Sphinx.add_directive(self, name, obj, content=content,  # pylint: disable=E1123
                                 arguments=arguments,
                                 override=override, **options)
        except TypeError:
            # Sphinx >= 3.0.0
            Sphinx.add_directive(self, name, obj, override=override, **options)
        except ExtensionError:  # pragma: no cover
            # Sphinx < 1.8
            Sphinx.add_directive(self, name, obj, content=content,  # pylint: disable=E1123
                                 arguments=arguments, **options)

    def add_domain(self, domain, override=True):
        self._added_objects.append(('domain', domain))
        try:
            # Sphinx >= 1.8
            Sphinx.add_domain(self, domain, override=override)
        except TypeError:  # pragma: no cover
            # Sphinx < 1.8
            Sphinx.add_domain(self, domain)
        # For some reason, the directives are missing from the main catalog
        # in docutils.
        for k, v in domain.directives.items():
            self.add_directive("{0}:{1}".format(domain.name, k), v)
            if domain.name in ('py', 'std', 'rst'):
                # We add the directive without the domain name as a prefix.
                self.add_directive(k, v)
        for k, v in domain.roles.items():
            self.add_role("{0}:{1}".format(domain.name, k), v)
            if domain.name in ('py', 'std', 'rst'):
                # We add the role without the domain name as a prefix.
                self.add_role(k, v)

    def override_domain(self, domain):
        self._added_objects.append(('domain-over', domain))
        try:
            Sphinx.override_domain(self, domain)
        except AttributeError:
            # Sphinx==3.0.0
            raise AttributeError(
                "override_domain not available in sphinx==3.0.0")

    def add_role(self, name, role, override=True):
        self._added_objects.append(('role', name))
        self.debug('[_CustomSphinx]  adding role: %r', (name, role))
        roles.register_local_role(name, role)

    def add_generic_role(self, name, nodeclass, override=True):
        self._added_objects.append(('generic_role', name))
        self.debug("[_CustomSphinx] adding generic role: '%r'",
                   (name, nodeclass))
        role = roles.GenericRole(name, nodeclass)
        roles.register_local_role(name, role)

    def add_node(self, node, override=True, **kwds):
        self._added_objects.append(('node', node))
        self.debug('[_CustomSphinx]  adding node: %r', (node, kwds))
        nodes._add_node_class_names([node.__name__])
        for key, val in kwds.items():
            try:
                visit, depart = val
            except ValueError:  # pragma: no cover
                raise ExtensionError(("Value for key '%r' must be a "
                                      "(visit, depart) function tuple") % key)
            translator = self.registry.translators.get(key)
            translators = []
            if translator is not None:
                translators.append(translator)
            elif key == 'html':
                from sphinx.writers.html import HTMLTranslator
                translators.append(HTMLTranslator)
                if is_html5_writer_available():
                    from sphinx.writers.html5 import HTML5Translator
                    translators.append(HTML5Translator)
            elif key == 'latex':
                translators.append(_get_LaTeXTranslator())
            elif key == 'elatex':
                translators.append(EnhancedLaTeXBuilder)
            elif key == 'text':
                from sphinx.writers.text import TextTranslator
                translators.append(TextTranslator)
            elif key == 'man':
                from sphinx.writers.manpage import ManualPageTranslator
                translators.append(ManualPageTranslator)
            elif key == 'texinfo':
                from sphinx.writers.texinfo import TexinfoTranslator
                translators.append(TexinfoTranslator)

            for translator in translators:
                setattr(translator, 'visit_' + node.__name__, visit)
                if depart:
                    setattr(translator, 'depart_' + node.__name__, depart)

    def add_event(self, name):
        self._added_objects.append(('event', name))
        Sphinx.add_event(self, name)

    def add_config_value(self, name, default, rebuild, types_=()):  # pylint: disable=W0221
        self._added_objects.append(('config_value', name))
        Sphinx.add_config_value(self, name, default, rebuild, types_)

    def add_directive_to_domain(self, domain, name, obj, has_content=None,  # pylint: disable=W0221
                                argument_spec=None, override=False, **option_spec):
        self._added_objects.append(('directive_to_domain', domain, name))
        try:
            Sphinx.add_directive_to_domain(self, domain, name, obj,  # pylint: disable=E1123
                                           has_content=has_content, argument_spec=argument_spec,
                                           override=override, **option_spec)
        except TypeError:  # pragma: no cover
            # Sphinx==3.0.0
            Sphinx.add_directive_to_domain(self, domain, name, obj,
                                           override=override, **option_spec)

    def add_role_to_domain(self, domain, name, role, override=False):
        self._added_objects.append(('roles_to_domain', domain, name))
        Sphinx.add_role_to_domain(self, domain, name, role, override=override)

    def add_transform(self, transform):
        self._added_objects.append(('transform', transform))
        Sphinx.add_transform(self, transform)

    def add_post_transform(self, transform):
        self._added_objects.append(('post_transform', transform))
        Sphinx.add_post_transform(self, transform)

    def add_js_file(self, filename, **kwargs):
        self._added_objects.append(('js', filename))
        try:
            # Sphinx >= 1.8
            Sphinx.add_js_file(self, filename, **kwargs)
        except AttributeError:  # pragma: no cover
            # Sphinx < 1.8
            Sphinx.add_javascript(self, filename, **kwargs)

    def add_css_file(self, filename, **kwargs):
        self._added_objects.append(('css', filename))
        try:
            # Sphinx >= 1.8
            Sphinx.add_css_file(self, filename, **kwargs)
        except AttributeError:  # pragma: no cover
            # Sphinx < 1.8
            Sphinx.add_stylesheet(self, filename, **kwargs)

    def add_latex_package(self, packagename, options=None, after_hyperref=False):
        self._added_objects.append(('latex', packagename))
        Sphinx.add_latex_package(
            self, packagename=packagename, options=options,
            after_hyperref=after_hyperref)

    def add_object_type(self, directivename, rolename, indextemplate='',
                        parse_node=None, ref_nodeclass=None, objname='',
                        doc_field_types=None, override=False):
        if doc_field_types is None:
            doc_field_types = []
        self._added_objects.append(('object', directivename, rolename))
        Sphinx.add_object_type(self, directivename, rolename, indextemplate=indextemplate,
                               parse_node=parse_node, ref_nodeclass=ref_nodeclass,
                               objname=objname, doc_field_types=doc_field_types,
                               override=override)

    def add_env_collector(self, collector):
        """
        See :epkg:`class Sphinx`.
        """
        self.debug(
            '[_CustomSphinx] adding environment collector: %r', collector)
        coll = collector()
        coll.enable(self)
        self._added_collectors.append(coll)

    def disconnect_env_collector(self, clname, exc=True):
        """
        Disables a collector given its class name.

        @param      cl      name
        @param      exc     raises an exception if not found
        @return             found collector
        """
        found = None
        foundi = None
        for i, co in enumerate(self._added_collectors):
            if clname == co.__class__.__name__:
                found = co
                foundi = i
                break
        if found is not None and not exc:
            return None
        if found is None:
            raise ValueError(  # pragma: no cover
                "Unable to find a collector '{0}' in \n{1}".format(
                    clname, "\n".join(
                        map(lambda x: x.__class__.__name__,
                            self._added_collectors))))
        for v in found.listener_ids.values():
            self.disconnect(v)
        del self._added_collectors[foundi]
        return found
