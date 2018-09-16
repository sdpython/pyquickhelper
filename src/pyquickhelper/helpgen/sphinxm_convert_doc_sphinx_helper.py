"""
@file
@brief Helpers to convert docstring to various format.

.. versionadded:: 1.3
"""
import os
import sys
from collections import deque
import warnings
import pickle
from sphinx.deprecation import RemovedInSphinx30Warning, RemovedInSphinx40Warning
from sphinx.locale import _
from docutils.parsers.rst import roles
from docutils.languages import en as docutils_en
from sphinx.writers.html import HTMLWriter
from sphinx.application import Sphinx, ENV_PICKLE_FILENAME
from sphinx.errors import ExtensionError
from sphinx.environment import BuildEnvironment
from docutils import nodes
from docutils.utils import Reporter
from sphinx.ext.extlinks import setup_link_roles
from sphinx.util.nodes import inline_all_toctrees
from sphinx.util.console import bold, darkgreen
from sphinx.util.docutils import WarningStream
from sphinx.util import status_iterator, logging
from sphinx.transforms import SphinxTransformer
from sphinx.util.osutil import relative_uri
from sphinx.util.logging import getLogger
from sphinx.util.docutils import is_html5_writer_available
from sphinx import __display_version__
from sphinx.application import Tags, builtin_extensions
from sphinx.application import Config, CONFIG_FILENAME, ConfigError, VersionRequirementError
from sphinx.registry import SphinxComponentRegistry
from sphinx.events import EventManager
from sphinx.locale import __
from sphinx import highlighting
from sphinx.environment.collectors.asset import logger as logger_asset
import sphinx.util.osutil
from .conf_path_tools import custom_ensuredir

try:
    # Sphinx 1.8.0
    from sphinx.extension import verify_needs_extensions as verify_extensions
    from sphinx.util.pycompat import htmlescape
except ImportError:
    # Sphinx 1.7.6
    from sphinx.extension import verify_required_extensions as verify_extensions

try:
    from sphinx.writers.latex import LaTeXTranslator
except ImportError:
    # Since sphinx 1.7.3 (circular reference).
    import sphinx.builders.latex.transforms
    from sphinx.writers.latex import LaTeXTranslator

from ..sphinxext.sphinx_bigger_extension import visit_bigger_node as ext_visit_bigger_node, depart_bigger_node as ext_depart_bigger_node
from ..sphinxext.sphinx_bigger_extension import visit_bigger_node_rst as ext_visit_bigger_node_rst
from ..sphinxext.sphinx_bigger_extension import depart_bigger_node_rst as ext_depart_bigger_node_rst
from ..sphinxext.sphinx_bigger_extension import depart_bigger_node_html as ext_depart_bigger_node_html
from ..sphinxext.sphinx_bigger_extension import depart_bigger_node_latex as ext_depart_bigger_node_latex
from ..sphinxext.sphinx_bigger_extension import visit_bigger_node_latex as ext_visit_bigger_node_latex
from ..sphinxext.sphinx_blocref_extension import visit_blocref_node as ext_visit_blocref_node, depart_blocref_node as ext_depart_blocref_node
from ..sphinxext.sphinx_blog_extension import visit_blogpost_node as ext_visit_blogpost_node, depart_blogpost_node as ext_depart_blogpost_node
from ..sphinxext.sphinx_blog_extension import visit_blogpostagg_node as ext_visit_blogpostagg_node
from ..sphinxext.sphinx_blog_extension import depart_blogpostagg_node as ext_depart_blogpostagg_node
from ..sphinxext.sphinx_blog_extension import depart_blogpostagg_node_html as ext_depart_blogpostagg_node_html
from ..sphinxext.sphinx_cmdref_extension import visit_cmdref_node as ext_visit_cmdref_node, depart_cmdref_node as ext_depart_cmdref_node
from ..sphinxext.sphinx_collapse_extension import visit_collapse_node as ext_visit_collapse_node
from ..sphinxext.sphinx_collapse_extension import depart_collapse_node as ext_depart_collapse_node
from ..sphinxext.sphinx_collapse_extension import visit_collapse_node_rst as ext_visit_collapse_node_rst
from ..sphinxext.sphinx_collapse_extension import depart_collapse_node_rst as ext_depart_collapse_node_rst
from ..sphinxext.sphinx_collapse_extension import depart_collapse_node_html as ext_depart_collapse_node_html
from ..sphinxext.sphinx_collapse_extension import visit_collapse_node_html as ext_visit_collapse_node_html
from ..sphinxext.sphinx_epkg_extension import visit_epkg_node as ext_visit_epkg_node, depart_epkg_node as ext_depart_epkg_node
from ..sphinxext.sphinx_exref_extension import visit_exref_node as ext_visit_exref_node, depart_exref_node as ext_depart_exref_node
from ..sphinxext.sphinx_faqref_extension import visit_faqref_node as ext_visit_faqref_node, depart_faqref_node as ext_depart_faqref_node
from ..sphinxext.sphinx_latex_builder import EnhancedLaTeXWriter, EnhancedLaTeXBuilder, EnhancedLaTeXTranslator
from ..sphinxext.sphinx_mathdef_extension import visit_mathdef_node as ext_visit_mathdef_node, depart_mathdef_node as ext_depart_mathdef_node
from ..sphinxext.sphinx_md_builder import MdWriter, MdBuilder, MdTranslator
from ..sphinxext.sphinx_nbref_extension import visit_nbref_node as ext_visit_nbref_node, depart_nbref_node as ext_depart_nbref_node
from ..sphinxext.sphinx_postcontents_extension import depart_postcontents_node as ext_depart_postcontents_node
from ..sphinxext.sphinx_postcontents_extension import visit_postcontents_node as ext_visit_postcontents_node
from ..sphinxext.sphinx_rst_builder import RstWriter, RstBuilder, RstTranslator

from ..sphinxext.sphinx_runpython_extension import visit_runpython_node as ext_visit_runpython_node
from ..sphinxext.sphinx_runpython_extension import depart_runpython_node as ext_depart_runpython_node
from ..sphinxext.sphinx_sharenet_extension import depart_sharenet_node as ext_depart_sharenet_node
from ..sphinxext.sphinx_sharenet_extension import depart_sharenet_node_html as ext_depart_sharenet_node_html
from ..sphinxext.sphinx_sharenet_extension import depart_sharenet_node_rst as ext_depart_sharenet_node_rst
from ..sphinxext.sphinx_sharenet_extension import visit_sharenet_node as ext_visit_sharenet_node
from ..sphinxext.sphinx_sharenet_extension import visit_sharenet_node_rst as ext_visit_sharenet_node_rst
from ..sphinxext.sphinx_todoext_extension import visit_todoext_node as ext_visit_todoext_node, depart_todoext_node as ext_depart_todoext_node
from ..sphinxext.sphinx_template_extension import visit_tpl_node as ext_visit_tpl_node, depart_tpl_node as ext_depart_tpl_node
from ..sphinxext.sphinx_tocdelay_extension import depart_tocdelay_node as ext_depart_tocdelay_node
from ..sphinxext.sphinx_tocdelay_extension import visit_tocdelay_node as ext_visit_tocdelay_node

from ..sphinxext.sphinx_video_extension import depart_video_node_html as ext_depart_video_node_html
from ..sphinxext.sphinx_video_extension import depart_video_node_rst as ext_depart_video_node_rst
from ..sphinxext.sphinx_video_extension import depart_video_node_latex as ext_depart_video_node_latex
from ..sphinxext.sphinx_video_extension import depart_video_node_text as ext_depart_video_node_text
from ..sphinxext.sphinx_video_extension import visit_video_node as ext_visit_video_node
from ..sphinxext.sphinx_youtube_extension import depart_youtube_node as ext_depart_youtube_node
from ..sphinxext.sphinx_youtube_extension import visit_youtube_node as ext_visit_youtube_node

from ..sphinxext.sphinx_image_extension import depart_simpleimage_node_html as ext_depart_simpleimage_node_html
from ..sphinxext.sphinx_image_extension import depart_simpleimage_node_rst as ext_depart_simpleimage_node_rst
from ..sphinxext.sphinx_image_extension import depart_simpleimage_node_md as ext_depart_simpleimage_node_md
from ..sphinxext.sphinx_image_extension import depart_simpleimage_node_latex as ext_depart_simpleimage_node_latex
from ..sphinxext.sphinx_image_extension import depart_simpleimage_node_text as ext_depart_simpleimage_node_text
from ..sphinxext.sphinx_image_extension import visit_simpleimage_node as ext_visit_simpleimage_node

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from sphinx.builders.html import SingleFileHTMLBuilder


if sys.version_info[0] == 2:
    from StringIO import StringIO
else:
    from io import StringIO

if is_html5_writer_available():
    from sphinx.writers.html5 import HTML5Translator as HTMLTranslator
else:
    from sphinx.writers.html import HTMLTranslator


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
        Tells if the translator is html format.
        """
        return self.base_class is HTMLTranslator

    def is_rst(self):
        """
        Tells if the translator is html format.
        """
        return self.base_class is RstTranslator

    def is_latex(self):
        """
        Tells if the translator is html format.
        """
        return self.base_class is LaTeXTranslator

    def visit_blogpost_node(self, node):
        """
        @see fn visit_blogpost_node
        """
        ext_visit_blogpost_node(self, node)

    def depart_blogpost_node(self, node):
        """
        @see fn depart_blogpost_node
        """
        ext_depart_blogpost_node(self, node)

    def visit_blogpostagg_node(self, node):
        """
        @see fn visit_blogpostagg_node
        """
        ext_visit_blogpostagg_node(self, node)

    def depart_blogpostagg_node(self, node):
        """
        @see fn depart_blogpostagg_node
        """
        if self.is_html():
            ext_depart_blogpostagg_node_html(self, node)
        else:
            ext_depart_blogpostagg_node(self, node)

    def visit_runpython_node(self, node):
        """
        @see fn visit_runpython_node
        """
        ext_visit_runpython_node(self, node)

    def depart_runpython_node(self, node):
        """
        @see fn depart_runpython_node
        """
        ext_depart_runpython_node(self, node)

    def visit_sharenet_node(self, node):
        """
        @see fn visit_sharenet_node
        """
        if self.is_html():
            ext_visit_sharenet_node(self, node)
        elif self.is_rst():
            ext_visit_sharenet_node_rst(self, node)
        else:
            ext_visit_sharenet_node(self, node)

    def depart_sharenet_node(self, node):
        """
        @see fn depart_sharenet_node
        """
        if self.is_html():
            ext_depart_sharenet_node_html(self, node)
        elif self.is_rst():
            ext_depart_sharenet_node_rst(self, node)
        else:
            ext_depart_sharenet_node(self, node)

    def visit_video_node(self, node):
        """
        @see fn visit_video_node
        """
        ext_visit_video_node(self, node)

    def depart_video_node_html(self, node):
        """
        @see fn depart_video_node_html
        """
        ext_depart_video_node_html(self, node)

    def depart_video_node_latex(self, node):
        """
        @see fn depart_video_node_latex
        """
        ext_depart_video_node_latex(self, node)

    def depart_video_node_text(self, node):
        """
        @see fn depart_video_node_text
        """
        ext_depart_video_node_text(self, node)

    def depart_video_node_rst(self, node):
        """
        @see fn depart_video_node_rst
        """
        ext_depart_video_node_rst(self, node)

    def visit_simpleimage_node(self, node):
        """
        @see fn visit_simpleimage_node
        """
        ext_visit_simpleimage_node(self, node)

    def depart_simpleimage_node_html(self, node):
        """
        @see fn depart_simpleimage_node_html
        """
        ext_depart_simpleimage_node_html(self, node)

    def depart_simpleimage_node_latex(self, node):
        """
        @see fn depart_simpleimage_node_latex
        """
        ext_depart_simpleimage_node_latex(self, node)

    def depart_simpleimage_node_text(self, node):
        """
        @see fn depart_simpleimage_node_text
        """
        ext_depart_simpleimage_node_text(self, node)

    def depart_simpleimage_node_md(self, node):
        """
        @see fn depart_simpleimage_node_md
        """
        ext_depart_simpleimage_node_md(self, node)

    def depart_simpleimage_node_rst(self, node):
        """
        @see fn depart_simpleimage_node_rst
        """
        ext_depart_simpleimage_node_rst(self, node)

    def visit_tpl_node(self, node):
        """
        @see fn visit_tpl_node
        """
        ext_visit_tpl_node(self, node)

    def depart_tpl_node(self, node):
        """
        @see fn depart_tpl_node
        """
        ext_depart_tpl_node(self, node)

    def visit_epkg_node(self, node):
        """
        @see fn visit_epkg_node
        """
        ext_visit_epkg_node(self, node)

    def depart_epkg_node(self, node):
        """
        @see fn depart_epkg_node
        """
        ext_depart_epkg_node(self, node)

    def visit_bigger_node(self, node):
        """
        @see fn visit_bigger_node
        """
        if self.is_rst():
            ext_visit_bigger_node_rst(self, node)
        elif self.is_latex():
            ext_visit_bigger_node_latex(self, node)
        else:
            ext_visit_bigger_node(self, node)

    def depart_bigger_node(self, node):
        """
        @see fn depart_bigger_node
        """
        if self.is_html():
            ext_depart_bigger_node_html(self, node)
        elif self.is_rst():
            ext_depart_bigger_node_rst(self, node)
        elif self.is_latex():
            ext_depart_bigger_node_latex(self, node)
        else:
            ext_depart_bigger_node(self, node)

    def visit_collapse_node(self, node):
        """
        @see fn visit_collapse_node
        """
        if self.is_html():
            ext_visit_collapse_node_html(self, node)
        elif self.is_rst():
            ext_visit_collapse_node_rst(self, node)
        else:
            ext_visit_collapse_node(self, node)

    def depart_collapse_node(self, node):
        """
        @see fn depart_collapse_node
        """
        if self.is_html():
            ext_depart_collapse_node_html(self, node)
        elif self.is_rst():
            ext_depart_collapse_node_rst(self, node)
        else:
            ext_depart_collapse_node(self, node)

    def visit_todoext_node(self, node):
        """
        @see fn visit_todoext_node
        """
        ext_visit_todoext_node(self, node)

    def depart_todoext_node(self, node):
        """
        @see fn depart_todoext_node
        """
        ext_depart_todoext_node(self, node)

    def visit_mathdef_node(self, node):
        """
        @see fn visit_mathdef_node
        """
        ext_visit_mathdef_node(self, node)

    def depart_mathdef_node(self, node):
        """
        @see fn depart_mathdef_node
        """
        ext_depart_mathdef_node(self, node)

    def visit_blocref_node(self, node):
        """
        @see fn visit_blocref_node
        """
        ext_visit_blocref_node(self, node)

    def depart_blocref_node(self, node):
        """
        @see fn depart_blocref_node
        """
        ext_depart_blocref_node(self, node)

    def visit_faqref_node(self, node):
        """
        @see fn visit_faqref_node
        """
        ext_visit_faqref_node(self, node)

    def depart_faqref_node(self, node):
        """
        @see fn depart_faqref_node
        """
        ext_depart_faqref_node(self, node)

    def visit_nbref_node(self, node):
        """
        @see fn visit_nbref_node
        """
        ext_visit_nbref_node(self, node)

    def depart_nbref_node(self, node):
        """
        @see fn depart_nbref_node
        """
        ext_depart_nbref_node(self, node)

    def visit_cmdref_node(self, node):
        """
        @see fn visit_cmdref_node
        """
        ext_visit_cmdref_node(self, node)

    def depart_cmdref_node(self, node):
        """
        @see fn depart_cmdref_node
        """
        ext_depart_cmdref_node(self, node)

    def visit_exref_node(self, node):
        """
        @see fn visit_exref_node
        """
        ext_visit_exref_node(self, node)

    def depart_exref_node(self, node):
        """
        @see fn depart_exref_node
        """
        ext_depart_exref_node(self, node)

    def add_secnumber(self, node):
        """
        overwrites this method to catch errors due when
        it is a single document being processed
        """
        if node.get('secnumber'):
            self.base_class.add_secnumber(self, node)
        elif len(node.parent['ids']) > 0:
            self.base_class.add_secnumber(self, node)
        else:
            n = len(self.builder.secnumbers)
            node.parent['ids'].append("custom_label_%d" % n)
            self.base_class.add_secnumber(self, node)

    def visit_pending_xref(self, node):
        # type: (nodes.Node) -> None
        self.visit_Text(node)
        raise nodes.SkipNode

    def depart_postcontents_node(self, node):
        """
        @see fn depart_postcontents_node
        """
        ext_depart_postcontents_node(self, node)

    def visit_postcontents_node(self, node):
        """
        @see fn visit_postcontents_node
        """
        ext_visit_postcontents_node(self, node)

    def depart_tocdelay_node(self, node):
        """
        @see fn depart_tocdelay_node
        """
        ext_depart_tocdelay_node(self, node)

    def visit_tocdelay_node(self, node):
        """
        @see fn visit_tocdelay_node
        """
        ext_visit_tocdelay_node(self, node)

    def depart_youtube_node(self, node):
        """
        @see fn depart_youtube_node
        """
        ext_depart_youtube_node(self, node)

    def visit_youtube_node(self, node):
        """
        @see fn visit_youtube_node
        """
        ext_visit_youtube_node(self, node)

    def eval_expr(self, expr):
        rst = self.output_format == 'rst'
        latex = self.output_format == 'latex'
        texinfo = [('index', 'A_AdditionalVisitDepart', 'B_AdditionalVisitDepart',   # pylint: disable=W0612
                    'C_AdditionalVisitDepart', 'D_AdditionalVisitDepart',
                    'E_AdditionalVisitDepart', 'Miscellaneous')]
        html = self.output_format == 'html'
        md = self.output_format == 'md'
        if not(rst or html or latex or md):
            raise ValueError(
                "Unknown output format '{0}'.".format(self.output_format))
        try:
            ev = eval(expr)
        except Exception:
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

    def unknown_visit(self, node):
        raise NotImplementedError("[HTMLTranslatorWithCustomDirectives] Unknown node: '{0}' in '{1}'".format(node.__class__.__name__,
                                                                                                             self.__class__.__name__))


class HTMLTranslatorWithCustomDirectives(_AdditionalVisitDepart, HTMLTranslator):
    """
    See @see cl HTMLWriterWithCustomDirectives.
    """

    def __init__(self, builder, *args, **kwds):
        """
        .. versionchanged:: 1.7
            Does something specific for HTML. only is a node.
        """
        HTMLTranslator.__init__(self, builder, *args, **kwds)
        _AdditionalVisitDepart.__init__(self, 'html')
        for name, f1, f2 in builder._function_node:
            setattr(self.__class__, "visit_" + name, f1)
            setattr(self.__class__, "depart_" + name, f2)
        self.base_class = HTMLTranslator

    def visit_field(self, node):
        # type: (nodes.Node) -> None
        if not hasattr(self, '_fieldlist_row_index'):
            # needed when a docstring starts with :param:
            self._fieldlist_row_index = 0
        return HTMLTranslator.visit_field(self, node)


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
            raise TypeError(
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

        ..versionchanged:: 1.5
            Parameter *app* was added.
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
        self.builder._function_node.append((name, f_visit, f_depart))

    def add_configuration_options(self, new_options):
        """
        add new options

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
        # type: () -> None
        # sadly, this is mostly copied from parent class
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
        Constructor

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
        Constructor

        @param      builder builder
        @param      app     Sphinx application
        """
        _WriterWithCustomDirectives._init(
            self, MdWriter, MDTranslatorWithCustomDirectives, app)

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
        Constructor

        @param      builder builder
        @param      app     Sphinx application
        """
        _WriterWithCustomDirectives._init(
            self, EnhancedLaTeXWriter, LatexTranslatorWithCustomDirectives, app)
        if not hasattr(self.builder, "config"):
            raise TypeError(
                "Builder has no config: {}".format(type(self.builder)))

    def translate(self):
        if not hasattr(self.builder, "config"):
            raise TypeError(
                "Builder has no config: {}".format(type(self.builder)))
        visitor = self.translator_class(self.builder, self.document)
        self.document.walkabout(visitor)
        self.output = visitor.body


class _MemoryBuilder:
    """
    Builds :epkg:`HTML` output in memory.
    The API is defined by the page
    `builderapi <http://www.sphinx-doc.org/en/stable/extdev/builderapi.html?highlight=builder>`_.
    """

    def _init(self, base_class, app):
        """
        Constructs the builder.
        Most of the parameter are static members of the class and cannot
        be overwritten (yet).

        :param base_class: base builder class
        :param app: `Sphinx application <http://www.sphinx-doc.org/en/stable/_modules/sphinx/application.html>`_
        """
        if "IMPOSSIBLE:TOFIND" in app.srcdir:
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
        with logging.pending_warnings():
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
        # type: (unicode, unicode) -> unicode
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
        ctx = self.globalcontext.copy()
        ctx['warn'] = self.warning if hasattr(self, "warning") else self.warn
        # current_page_name is backwards compatibility
        ctx['pagename'] = ctx['current_page_name'] = pagename
        ctx['encoding'] = self.config.html_output_encoding
        default_baseuri = self.get_target_uri(pagename)
        # in the singlehtml builder, default_baseuri still contains an #anchor
        # part, which relative_uri doesn't really like...
        default_baseuri = default_baseuri.rsplit('#', 1)[0]

        def pathto(otheruri, resource=False, baseuri=default_baseuri):
            # type: (unicode, bool, unicode) -> unicode
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
            # type: (Stylesheet) -> unicode
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
            # type: (unicode) -> bool
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
        except UnicodeError:
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


class MemoryHTMLBuilder(_MemoryBuilder, SingleFileHTMLBuilder):
    """
    Builds :epkg:`HTML` output in memory.
    The API is defined by the page
    `builderapi <http://www.sphinx-doc.org/en/stable/extdev/builderapi.html?highlight=builder>`_.
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

        :param app: `Sphinx application <http://www.sphinx-doc.org/en/stable/_modules/sphinx/application.html>`_
        """
        _MemoryBuilder._init(self, SingleFileHTMLBuilder, app)


class MemoryRSTBuilder(_MemoryBuilder, RstBuilder):

    """
    Builds :epkg:`RST` output in memory.
    The API is defined by the page
    `builderapi <http://www.sphinx-doc.org/en/stable/extdev/builderapi.html?highlight=builder>`_.
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

        :param app: `Sphinx application <http://www.sphinx-doc.org/en/stable/_modules/sphinx/application.html>`_
        """
        _MemoryBuilder._init(self, RstBuilder, app)

    def handle_page(self, pagename, addctx, templatename=None,
                    outfilename=None, event_arg=None):
        """
        Override *handle_page* to write into stream instead of files.
        """
        if templatename is not None:
            raise NotImplementedError("templatename must be None.")
        if not outfilename:
            outfilename = self.get_outfilename(pagename)
        if outfilename not in self.built_pages:
            self.built_pages[outfilename] = StringIO()
        self.built_pages[outfilename].write(self.writer.output)


class MemoryMDBuilder(_MemoryBuilder, MdBuilder):
    """
    Builds :epkg:`MD` output in memory.
    The API is defined by the page
    `builderapi <http://www.sphinx-doc.org/en/stable/extdev/builderapi.html?highlight=builder>`_.
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

        :param app: `Sphinx application <http://www.sphinx-doc.org/en/stable/_modules/sphinx/application.html>`_
        """
        _MemoryBuilder._init(self, MdBuilder, app)

    def handle_page(self, pagename, addctx, templatename=None,
                    outfilename=None, event_arg=None):
        """
        Override *handle_page* to write into stream instead of files.
        """
        if templatename is not None:
            raise NotImplementedError("templatename must be None.")
        if not outfilename:
            outfilename = self.get_outfilename(pagename)
        if outfilename not in self.built_pages:
            self.built_pages[outfilename] = StringIO()
        self.built_pages[outfilename].write(self.writer.output)


class MemoryLatexBuilder(_MemoryBuilder, EnhancedLaTeXBuilder):
    """
    Builds :epkg:`Latex` output in memory.
    The API is defined by the page
    `builderapi <http://www.sphinx-doc.org/en/stable/extdev/builderapi.html?highlight=builder>`_.
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
        Construct the builder.
        Most of the parameter are static members of the class and cannot
        be overwritten (yet).

        :param app: `Sphinx application <http://www.sphinx-doc.org/en/stable/_modules/sphinx/application.html>`_
        """
        _MemoryBuilder._init(self, EnhancedLaTeXBuilder, app)

    def write_stylesheet(self):
        # type: () -> None
        highlighter = highlighting.PygmentsBridge(
            'latex', self.config.pygments_style)
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
            raise TypeError(
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
        # type: (unicode) -> nodes.Node
        """Read the doctree for a file from the pickle and return it."""
        if hasattr(self, "doctree_") and docname in self.doctree_:
            doctree = self.doctree_[docname]
            doctree.settings.env = self
            doctree.reporter = Reporter(self.doc2path(
                docname), 2, 5, stream=WarningStream())
            return doctree
        else:
            if hasattr(self, "self.doctree_"):
                available = list(sorted(self.doctree_))
                if len(available) > 10:
                    available = available[10:]
            else:
                available = []

            raise KeyError("Unable to find doctree for '{0}'\nFirst documents:\n{1}.".format(
                docname, "\n".join(available)))
            # return BuildEnvironment.get_doctree(self, docname)

    def apply_post_transforms(self, doctree, docname):
        # type: (nodes.Node, unicode) -> None
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
                 confoverrides=None, status=None, freshenv=False, warningiserror=False,
                 tags=None, verbosity=0, parallel=0, new_extensions=None):
        '''
        Constructor. Same constructor as
        `sphinx application <http://www.sphinx-doc.org/en/stable/extdev/appapi.html>`_,
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
            'md': ('md', 'MdBuilder')}
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

        if doctreedir is None:
            doctreedir = "IMPOSSIBLE:TOFIND"
        if srcdir is None:
            srcdir = "IMPOSSIBLE:TOFIND"
        update_docutils_languages()
        self.verbosity = verbosity

        # type: Dict[unicode, Extension]
        self.extensions = {}
        self._setting_up_extension = ['?']      # type: List[unicode]
        self.builder = None                     # type: Builder
        self.env = None                         # type: BuildEnvironment
        self.registry = SphinxComponentRegistry()
        self.post_transforms = []               # type: List[Transform]
        self.html_themes = {}                   # type: Dict[unicode, unicode]

        self.srcdir = srcdir
        self.confdir = confdir
        self.outdir = outdir
        self.doctreedir = doctreedir

        self.parallel = parallel

        if status is None:
            self._status = StringIO()      # type: IO
            self.quiet = True
        else:
            self._status = status
            self.quiet = False

        # warning = confoverrides.get('warning_stream', None)
        # if warning is None:
        #    self._warning = StringIO()     # type: IO
        # else:
        #    self._warning = warning
        # self._warncount = 0
        # self.warningiserror = warningiserror
        # logging.setup(self, self._status, self._warning)

        self.events = EventManager()

        # keep last few messages for traceback
        # This will be filled by sphinx.util.logging.LastMessagesWriter
        self.messagelog = deque(maxlen=10)  # type: deque

        # say hello to the world
        self.info(bold('Running Sphinx v%s' % __display_version__))

        # status code for command-line application
        self.statuscode = 0

        # read config
        self.tags = Tags(tags)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RemovedInSphinx30Warning)
            warnings.simplefilter("ignore", RemovedInSphinx40Warning)
            self.config = Config(confdir, CONFIG_FILENAME,
                                 confoverrides or {}, self.tags)
        self.sphinx__display_version__ = __display_version__

        # create the environment
        self.env = _CustomBuildEnvironment(self)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RemovedInSphinx30Warning)
            warnings.simplefilter("ignore", RemovedInSphinx40Warning)
            warnings.simplefilter("ignore", ImportWarning)
            self.config.check_unicode()
        self.config.pre_init_values()

        # set up translation infrastructure
        self._init_i18n()

        # check the Sphinx version if requested
        if self.config.needs_sphinx and self.config.needs_sphinx > __display_version__:
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
            except Exception as e:
                mes = "Unable to run setup_extension '{0}'\nWHOLE LIST\n{1}".format(
                    extension, "\n".join(builtin_extensions))
                raise ExtensionError(mes) from e

        # load all user-given extension modules
        for extension in self.config.extensions:
            self.setup_extension(extension)

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

        if isinstance(buildername, tuple):
            if len(buildername) != 2:
                raise ValueError(
                    "The builder can be custom but it must be specifed as a 2-uple=(builder_name, builder_class).")
            self.add_builder(buildername[1])
            buildername = buildername[0]

        # preload builder module (before init config values)
        self.preload_builder(buildername)

        # the config file itself can be an extension
        if self.config.setup:
            if hasattr(self.config.setup, '__call__'):
                self.config.setup(self)
            else:
                raise ConfigError(
                    _("'setup' as currently defined in conf.py isn't a Python callable. "
                      "Please modify its definition to make it a callable function. This is "
                      "needed for conf.py to behave as a Sphinx extension.")
                )

        # now that we know all config values, collect them from conf.py
        noallowed = []
        rem = []
        for k in confoverrides:
            if k in {'initial_header_level', 'doctitle_xform', 'input_encoding',
                     'outdir', 'warnings_log'}:
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
            raise ValueError("The following configuration values are declared in any extension.\n{0}\n--DECLARED--\n{1}".format(
                "\n".join(sorted(noallowed)),
                "\n".join(sorted(self.config.values))))
        self.config.init_values()
        self.emit('config-inited', self.config)

        # check extension versions if requested
        # self.config.needs_extensions = self.config.extensions
        verify_extensions(self, self.config)

        # check primary_domain if requested
        primary_domain = self.config.primary_domain
        if primary_domain and not self.registry.has_domain(primary_domain):
            self.warning(
                _('primary_domain %r not found, ignored.'), primary_domain)

        # create the builder
        self.builder = self.create_builder(buildername)
        # check all configuration values for permissible types
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RemovedInSphinx30Warning)
            warnings.simplefilter("ignore", RemovedInSphinx40Warning)
            self.config.check_types()
        # set up the build environment
        self._init_env(freshenv)
        # set up the builder
        self._init_builder()

        # set up the build environment
        if freshenv:
            self._init_env(freshenv)
        else:
            for domain in self.registry.create_domains(self.env):
                self.env.domains[domain.name] = domain

        if not isinstance(self.env, _CustomBuildEnvironment):
            raise TypeError(
                "self.env is not _CustomBuildEnvironment: '{0}' buildername='{1}'".format(type(self.env), buildername))

        # addition
        self._extended_init_()

    def _init_env(self, freshenv):
        # type: (bool) -> None
        if freshenv:
            self.env = _CustomBuildEnvironment(self)
            self.env.setup(self)
            if self.srcdir is not None and self.srcdir != "IMPOSSIBLE:TOFIND":
                self.env.find_files(self.config, self.builder)
        else:
            filename = os.path.join(self.doctreedir, ENV_PICKLE_FILENAME)
            try:
                self.info(bold(__('loading pickled environment... ')), nonl=True)
                with open(filename, 'rb') as f:
                    self.env = pickle.load(f)
                    self.env.setup(self)
                self.info(__('done'))
            except Exception as err:
                self.info('failed: %s' % err)
                self._init_env(freshenv=True)

    def create_builder(self, name):
        """
        Creates a builder, raises an exception if name is None.
        """
        if name is None:
            raise ValueError("Builder name cannot be None")

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
            raise TypeError(
                "self.env is not _CustomBuildEnvironment: '{0}'".format(type(self.env)))
        if not isinstance(self.builder.env, _CustomBuildEnvironment):
            raise TypeError("self.builder.env is not _CustomBuildEnvironment: '{0}'".format(
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
        logger_asset.setLevel(40)  # only errors
        self.emit('doctree-read', doctree)
        logger_asset.setLevel(30)  # back to warnings

        for img in imgs:
            img['uri'] = img['save_uri']

        self.emit('doctree-resolved', doctree, self.config.master_doc)
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
            self.registry.add_builder(builder, override=override)
        else:
            self.debug('[_CustomSphinx]  already added builder: %r', builder)

    def setup_extension(self, extname):
        self._added_objects.append(('extension', extname))
        self.debug('[_CustomSphinx]  setting up extension: %r', extname)
        try:
            with warnings.catch_warnings():
                warnings.filterwarnings(
                    "ignore", category=DeprecationWarning)
                warnings.filterwarnings(
                    "ignore", category=RemovedInSphinx30Warning)
                self.registry.load_extension(self, extname)
        except Exception as e:
            raise ExtensionError(
                "Unable to setup extension '{0}'".format(extname)) from e

    def add_directive(self, name, obj, content=None, arguments=None, override=True, **options):
        self._added_objects.append(('directive', name))
        Sphinx.add_directive(self, name, obj, content=content, arguments=arguments,
                             override=override, **options)

    def add_domain(self, domain, override=True):
        self._added_objects.append(('domain', domain))
        Sphinx.add_domain(self, domain, override=override)
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
        Sphinx.override_domain(self, domain)

    def add_role(self, name, role, override=True):
        self._added_objects.append(('role', name))
        self.debug('[_CustomSphinx]  adding role: %r', (name, role))
        if name in roles._roles and not override:
            self.warning(_('[_CustomSphinx] while setting up extension %s: role %r is '
                           'already registered, it will be overridden'),
                         self._setting_up_extension[-1], name,
                         type='app', subtype='add_role')
        roles.register_local_role(name, role)

    def add_generic_role(self, name, nodeclass, override=True):
        self._added_objects.append(('generic_role', name))
        self.debug('[_CustomSphinx] adding generic role: %r',
                   (name, nodeclass))
        if name in roles._roles and not override:
            self.warning(_('[_CustomSphinx] while setting up extension %s: role %r is '
                           'already registered, it will be overridden'),
                         self._setting_up_extension[-1], name,
                         type='app', subtype='add_generic_role')
        role = roles.GenericRole(name, nodeclass)
        roles.register_local_role(name, role)

    def add_node(self, node, override=True, **kwds):
        self._added_objects.append(('node', node))
        self.debug('[_CustomSphinx]  adding node: %r', (node, kwds))
        if not override and hasattr(nodes.GenericNodeVisitor, 'visit_' + node.__name__):
            self.warning(_('[_CustomSphinx] while setting up extension %s: node class %r is '
                           'already registered, its visitors will be overridden'),
                         self._setting_up_extension, node.__name__,
                         type='app', subtype='add_node')
        nodes._add_node_class_names([node.__name__])
        for key, val in kwds.items():
            try:
                visit, depart = val
            except ValueError:
                raise ExtensionError(_('Value for key %r must be a '
                                       '(visit, depart) function tuple') % key)
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
                try:
                    from sphinx.writers.latex import LaTeXTranslator
                except ImportError:
                    # Since sphinx 1.7.3 (circular reference).
                    import sphinx.builders.latex.transforms  # pylint: disable=W0621
                    from sphinx.writers.latex import LaTeXTranslator
                translators.append(LaTeXTranslator)
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

    def add_directive_to_domain(self, domain, name, obj, has_content=None,
                                argument_spec=None, override=False, **option_spec):
        self._added_objects.append(('directive_to_domain', domain, name))
        Sphinx.add_directive_to_domain(self, domain, name, obj,
                                       has_content=has_content, argument_spec=argument_spec,
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

    def add_javascript(self, filename, **kwargs):
        self._added_objects.append(('js', filename))
        Sphinx.add_javascript(self, filename, **kwargs)

    def add_stylesheet(self, filename, alternate=False, title=None):
        self._added_objects.append(('css', filename))
        Sphinx.add_stylesheet(self, filename)

    def add_latex_package(self, packagename, options=None):
        self._added_objects.append(('latex', packagename))
        Sphinx.add_latex_package(self, packagename)

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
            raise ValueError("Unable to find a collector '{0}' in \n{1}".format(
                clname, "\n".join(map(lambda x: x.__class__.__name__, self._added_collectors))))
        for v in found.listener_ids.values():
            self.disconnect(v)
        del self._added_collectors[foundi]
        return found
