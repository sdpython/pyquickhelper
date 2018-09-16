# -*- coding: utf-8 -*-
"""
@file
@brief Overwrites latex writer as Sphinx's version is bugged in version 1.8.0.
"""
import os
from docutils import nodes
from docutils.frontend import OptionParser
from sphinx.locale import __
from sphinx.builders.latex import LaTeXBuilder
from sphinx.writers.latex import LaTeXWriter, LaTeXTranslator
from sphinx.writers.latex import ENUMERATE_LIST_STYLE, toRoman, rstdim_to_latexdim
from sphinx.util import logging
from sphinx.util.docutils import SphinxFileOutput
from sphinx import addnodes

from .sphinx_autosignature import depart_autosignature_node, visit_autosignature_node
from .sphinx_bigger_extension import depart_bigger_node_latex, visit_bigger_node_latex
from .sphinx_blocref_extension import visit_blocref_node, depart_blocref_node
from .sphinx_blog_extension import visit_blogpost_node, depart_blogpost_node
from .sphinx_blog_extension import visit_blogpostagg_node, depart_blogpostagg_node
from .sphinx_cmdref_extension import visit_cmdref_node, depart_cmdref_node
from .sphinx_collapse_extension import visit_collapse_node, depart_collapse_node
from .sphinx_epkg_extension import visit_epkg_node, depart_epkg_node
from .sphinx_exref_extension import visit_exref_node, depart_exref_node
from .sphinx_faqref_extension import visit_faqref_node, depart_faqref_node
from .sphinx_mathdef_extension import visit_mathdef_node, depart_mathdef_node
from .sphinx_nbref_extension import visit_nbref_node, depart_nbref_node
from .sphinx_postcontents_extension import depart_postcontents_node, visit_postcontents_node
from .sphinx_runpython_extension import visit_runpython_node, depart_runpython_node
from .sphinx_sharenet_extension import depart_sharenet_node, visit_sharenet_node
from .sphinx_todoext_extension import visit_todoext_node, depart_todoext_node
from .sphinx_template_extension import visit_tpl_node, depart_tpl_node
from .sphinx_tocdelay_extension import depart_tocdelay_node, visit_tocdelay_node
from .sphinx_video_extension import depart_video_node_latex, visit_video_node
from .sphinx_youtube_extension import depart_youtube_node, visit_youtube_node
from .sphinx_image_extension import depart_simpleimage_node_latex, visit_simpleimage_node


class EnhancedLaTeXTranslator(LaTeXTranslator):
    """
    Overwrites `LaTeXTranslator <https://github.com/sphinx-doc/sphinx/blob/master/sphinx/writers/latex.py#L451>`_
    and modifies a few functions.
    """

    def __init__(self, builder, document):
        if not hasattr(builder, "config"):
            raise TypeError("Builder has no config: {}".format(type(builder)))
        LaTeXTranslator.__init__(self, document, builder)

        newlines = builder.config.text_newlines
        if newlines == 'windows':
            self.nl = '\r\n'
        elif newlines == 'native':
            self.nl = os.linesep
        else:
            self.nl = '\n'

    def add_text(self, line):
        self.body.append(line)

    def visit_document(self, node):
        LaTeXTranslator.visit_document(self, node)

    def visit_enumerated_list(self, node):
        # type: (nodes.Node) -> None
        def get_enumtype(node):
            # type: (nodes.Node) -> unicode
            enumtype = node.get('enumtype', 'arabic')
            if 'alpha' in enumtype and 26 < node.get('start', 0) + len(node):  # pylint: disable=C0122
                # fallback to arabic if alphabet counter overflows
                enumtype = 'arabic'

            return enumtype

        def get_nested_level(node):
            # type: (nodes.Node) -> int
            if node is None:
                return 0
            elif isinstance(node, nodes.enumerated_list):
                return get_nested_level(node.parent) + 1
            else:
                return get_nested_level(node.parent)

        enum = "enum%s" % toRoman(get_nested_level(node)).lower()
        enumnext = "enum%s" % toRoman(get_nested_level(node) + 1).lower()
        style = ENUMERATE_LIST_STYLE.get(get_enumtype(node))

        self.body.append('\\begin{enumerate}\n')
        self.body.append('\\def\\the%s{%s{%s}}\n' % (enum, style, enum))
        prefix = node['prefix'] if 'prefix' in node else ''
        suffix = node['suffix'] if 'suffix' in node else ''
        self.body.append('\\def\\label%s{%s\\the%s %s}\n' %
                         (enum, prefix, enum, suffix))
        self.body.append('\\makeatletter\\def\\p@%s{\\p@%s %s\\the%s %s}\\makeatother\n' %
                         (enumnext, enum, prefix, enum, suffix))
        if 'start' in node:
            self.body.append('\\setcounter{%s}{%d}\n' %
                             (enum, node['start'] - 1))
        if self.table:
            self.table.has_problematic = True

    def eval_expr(self, expr):
        md = False
        rst = True
        html = False
        latex = False
        if not(rst or html or latex or md):
            raise ValueError("One of them should be True")
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

    def latex_image_length(self, width_str):
        # type: (nodes.Node) -> unicode
        try:
            return rstdim_to_latexdim(width_str)
        except ValueError:
            if width_str == 'auto':
                pass
            else:
                self.builder.logger.warning(
                    __('[EnhancedLaTeXTranslator] dimension unit %s is invalid. Ignored.'), width_str)
            return None

    def visit_inheritance_diagram(self, node):
        pass

    def depart_inheritance_diagram(self, node):
        pass

    def unknown_visit(self, node):
        # type: (nodes.Node) -> None
        raise NotImplementedError("Unknown node '{0}' detected in '{1}'".format(
            node.__class__.__name__, self.__class__.__name__))

    def depart_autosignature_node(self, node):
        depart_autosignature_node(self, node)

    def visit_autosignature_node(self, node):
        visit_autosignature_node(self, node)

    def depart_bigger_node(self, node):
        return depart_bigger_node_latex(self, node)

    def visit_bigger_node(self, node):
        visit_bigger_node_latex(self, node)

    def visit_blocref_node(self, node):
        visit_blocref_node(self, node)

    def depart_blocref_node(self, node):
        depart_blocref_node(self, node)

    def visit_blogpost_node(self, node):
        visit_blogpost_node(self, node)

    def depart_blogpost_node(self, node):
        depart_blogpost_node(self, node)

    def visit_blogpostagg_node(self, node):
        visit_blogpostagg_node(self, node)

    def depart_blogpostagg_node(self, node):
        depart_blogpostagg_node(self, node)

    def visit_cmdref_node(self, node):
        visit_cmdref_node(self, node)

    def depart_cmdref_node(self, node):
        depart_cmdref_node(self, node)

    def visit_collapse_node(self, node):
        visit_collapse_node(self, node)

    def depart_collapse_node(self, node):
        depart_collapse_node(self, node)

    def visit_epkg_node(self, node):
        visit_epkg_node(self, node)

    def depart_epkg_node(self, node):
        depart_epkg_node(self, node)

    def visit_exref_node(self, node):
        visit_exref_node(self, node)

    def depart_exref_node(self, node):
        depart_exref_node(self, node)

    def visit_faqref_node(self, node):
        visit_faqref_node(self, node)

    def depart_faqref_node(self, node):
        depart_faqref_node(self, node)

    def visit_mathdef_node(self, node):
        visit_mathdef_node(self, node)

    def depart_mathdef_node(self, node):
        depart_mathdef_node(self, node)

    def visit_nbref_node(self, node):
        visit_nbref_node(self, node)

    def depart_nbref_node(self, node):
        depart_nbref_node(self, node)

    def depart_postcontents_node(self, node):
        depart_postcontents_node(self, node)

    def visit_postcontents_node(self, node):
        visit_postcontents_node(self, node)

    def visit_runpython_node(self, node):
        visit_runpython_node(self, node)

    def depart_runpython_node(self, node):
        depart_runpython_node(self, node)

    def visit_sharenet_node(self, node):
        visit_sharenet_node(self, node)

    def depart_sharenet_node(self, node):
        depart_sharenet_node(self, node)

    def visit_todoext_node(self, node):
        visit_todoext_node(self, node)

    def depart_todoext_node(self, node):
        depart_todoext_node(self, node)

    def visit_tpl_node(self, node):
        visit_tpl_node(self, node)

    def depart_tpl_node(self, node):
        depart_tpl_node(self, node)

    def depart_tocdelay_node(self, node):
        depart_tocdelay_node(self, node)

    def visit_tocdelay_node(self, node):
        visit_tocdelay_node(self, node)

    def depart_video_node(self, node):
        depart_video_node_latex(self, node)

    def visit_video_node(self, node):
        visit_video_node(self, node)

    def depart_youtube_node(self, node):
        depart_youtube_node(self, node)

    def visit_youtube_node(self, node):
        visit_youtube_node(self, node)

    def depart_simpleimage_node(self, node):
        depart_simpleimage_node_latex(self, node)

    def visit_simpleimage_node(self, node):
        visit_simpleimage_node(self, node)


class EnhancedLaTeXWriter(LaTeXWriter):
    """
    Overwrites `LatexWriter <https://github.com/sphinx-doc/sphinx/blob/master/sphinx/writers/latex.py#L189>`_.
    """
    translator_class = EnhancedLaTeXTranslator

    def __init__(self, builder):
        LaTeXWriter.__init__(self, builder)
        if not hasattr(builder, "config"):
            raise TypeError("Builder has no config: {}".format(type(builder)))

    def translate(self):
        visitor = EnhancedLaTeXTranslator(self.builder, self.document)
        self.document.walkabout(visitor)
        self.output = visitor.body


class EnhancedLaTeXBuilder(LaTeXBuilder):
    """
    Overwrites `LaTeXBuilder <https://github.com/sphinx-doc/sphinx/blob/master/sphinx/builders/latex/__init__.py>`_.
    """
    name = 'elatex'
    format = 'latex'
    file_suffix = '.tex'
    epilog = __('The EnhancedTexinfo files are in %(outdir)s.')
    if os.name == 'posix':
        epilog += __("\nRun 'make' in that directory to run these through "
                     "makeinfo\n"
                     "(use 'make info' here to do that automatically).")

    supported_image_types = ['image/png', 'image/jpeg', 'image/gif']
    default_translator_class = EnhancedLaTeXTranslator

    def __init__(self, *args, **kwargs):
        """
        Constructor, add a logger.
        """
        LaTeXBuilder.__init__(self, *args, **kwargs)
        self.logger = logging.getLogger("EnhancedLatexBuilder")
        self._memo_pages = {}

    def get_outfilename(self, pagename):
        """
        Overwrites *get_target_uri* to control file names.
        """
        return "{0}/{1}.tex".format(self.outdir, pagename).replace("\\", "/")

    def finish(self):
        pass

    def _get_filename(self, targetname, encoding='utf-8', overwrite_if_changed=True):
        return SphinxFileOutput(destination_path=os.path.join(self.outdir, targetname),
                                encoding=encoding, overwrite_if_changed=overwrite_if_changed)

    def write(self, *ignored):
        # type: (Any) -> None
        docwriter = EnhancedLaTeXWriter(self)
        docsettings = OptionParser(
            defaults=self.env.settings,
            components=(docwriter,),
            read_config_files=True).get_default_values()

        self.init_document_data()
        self.write_stylesheet()

        for entry in self.document_data:
            docname, targetname, title, author, docclass = entry[:5]
            toctree_only = False
            if len(entry) > 5:
                toctree_only = entry[5]
            destination = self._get_filename(targetname, encoding='utf-8',
                                             overwrite_if_changed=True)
            self.logger.info(__("processing %s..."), targetname, nonl=1)
            toctrees = self.env.get_doctree(docname).traverse(addnodes.toctree)
            if toctrees:
                if toctrees[0].get('maxdepth') > 0:
                    tocdepth = toctrees[0].get('maxdepth')
                else:
                    tocdepth = None
            else:
                tocdepth = None
            doctree = self.assemble_doctree(
                docname, toctree_only,
                appendices=((docclass != 'howto') and self.config.latex_appendices or []))
            doctree['tocdepth'] = tocdepth
            self.apply_transforms(doctree)
            self.post_process_images(doctree)
            self.logger.info(__("writing... "), nonl=1)
            doctree.settings = docsettings
            doctree.settings.author = author
            doctree.settings.title = title
            doctree.settings.contentsname = self.get_contentsname(docname)
            doctree.settings.docname = docname
            doctree.settings.docclass = docclass
            docwriter.write(doctree, destination)
            self.logger.info("done")


def setup(app):
    """
    Initializes builder @see cl EnhancedLaTeXBuilder.
    """
    app.add_builder(EnhancedLaTeXBuilder)
