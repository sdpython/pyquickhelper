# -*- coding: utf-8 -*-
"""
@file
@brief Overwrites latex writer as Sphinx's version is bugged in version 1.8.0.

.. versionadded:: 1.8
"""
import os
from docutils import nodes
from docutils.frontend import OptionParser
from sphinx.locale import __
from sphinx.builders.latex import LaTeXBuilder
from sphinx.writers.latex import (
    LaTeXWriter, LaTeXTranslator, rstdim_to_latexdim)
from sphinx.util import logging
from sphinx import addnodes
from sphinx.writers.latex import toRoman, ENUMERATE_LIST_STYLE
from sphinx.util.docutils import SphinxFileOutput
from sphinx.util.template import LaTeXRenderer


class CustomizedSphinxFileOutput(SphinxFileOutput):
    """Customized FileOutput class for :epkg:`Sphinx`."""

    def __init__(self, **kwargs):
        SphinxFileOutput.__init__(self, **kwargs)

    def write(self, data):
        res = SphinxFileOutput.write(self, data)
        return res


class EnhancedLaTeXTranslator(LaTeXTranslator):
    """
    Overwrites `LaTeXTranslator <https://github.com/sphinx-doc/sphinx/blob/master/sphinx/writers/latex.py#L451>`_
    and modifies a few functions.
    """

    def __init__(self, builder, document):
        if not hasattr(builder, 'config'):
            raise TypeError(
                "Unexpected type for builder {0}".format(type(builder)))
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

        def get_enumtype(node):
            enumtype = node.get('enumtype', 'arabic')
            if 'alpha' in enumtype and 26 < node.get('start', 0) + len(node):  # pylint: disable=C0122
                # fallback to arabic if alphabet counter overflows
                enumtype = 'arabic'

            return enumtype

        def get_nested_level(node):
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

    def latex_image_length(self, width_str, scale=100):
        try:
            return rstdim_to_latexdim(width_str, scale)
        except ValueError:
            if width_str == 'auto':
                pass
            else:
                self.builder.logger.warning(
                    __('[EnhancedLaTeXTranslator] dimension unit %s is invalid. Ignored.'), width_str)
            return None
        except TypeError:
            # Sphinx <= 1.7
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

    def render(self, template_name, variables):
        renderer = LaTeXRenderer(latex_engine=self.config.latex_engine)
        if self.builder.config.templates_path is None:
            tpls = [os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                 "templates")]
        else:
            tpls = self.builder.config.templates_path
        for template_dir in tpls:
            if os.path.exists(template_dir):
                template = os.path.join(template_dir, template_name)
            else:
                template = os.path.join(self.builder.confdir, template_dir,
                                        template_name)
            if os.path.exists(template):
                return renderer.render(template, variables)

        return renderer.render(template_name, variables)

    def unknown_visit(self, node):
        raise NotImplementedError("Unknown node '{0}' detected in '{1}'".format(
            node.__class__.__name__, self.__class__.__name__))


class EnhancedLaTeXWriter(LaTeXWriter):
    """
    Overwrites `LatexWriter <https://github.com/sphinx-doc/sphinx/blob/master/sphinx/writers/latex.py#L189>`_.
    """
    translator_class = EnhancedLaTeXTranslator

    def __init__(self, builder):
        if not hasattr(builder, "config"):
            raise TypeError("Builder has no config: {}".format(type(builder)))
        LaTeXWriter.__init__(self, builder)

    def translate(self):
        visitor = self.builder.create_translator(self.builder, self.document)
        self.document.walkabout(visitor)
        self.output = visitor.astext()


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
        self._skip_finish = self.app.config.elatex_bypass_finish

    def finish(self):
        if self._skip_finish:
            return None
        else:
            return LaTeXBuilder.finish(self)

    def get_outfilename(self, pagename):
        """
        Overwrites *get_target_uri* to control file names.
        """
        return "{0}/{1}.tex".format(self.outdir, pagename).replace("\\", "/")

    def _get_filename(self, targetname, encoding='utf-8', overwrite_if_changed=True):
        return CustomizedSphinxFileOutput(destination_path=os.path.join(self.outdir, targetname),
                                          encoding=encoding, overwrite_if_changed=overwrite_if_changed)

    def write(self, *ignored):
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
            self.logger.info(
                "[EnhancedLaTeXBuilder] done in '{}'".format(targetname))


def setup(app):
    """
    Initializes builder @see cl EnhancedLaTeXBuilder.
    """
    app.add_config_value('elatex_bypass_finish', False, 'elatex')
    app.add_builder(EnhancedLaTeXBuilder)
