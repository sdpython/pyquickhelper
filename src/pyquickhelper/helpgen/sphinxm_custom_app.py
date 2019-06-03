# -*- coding: utf-8 -*-
"""
@file
@brief Inspired from module
`sphinx-testing <https://github.com/sphinx-doc/sphinx-testing/>`_
"""
import shutil
import os
import warnings
from io import StringIO
from sphinx.application import Sphinx
from .default_conf import latex_preamble


class CustomSphinxApp(Sphinx):
    """
    A subclass of class *Sphinx*,
    the goal is to interpret :epkg:`RST` with custom directives.
    """

    def __init__(self, srcdir, outdir, confdir=None, doctreedir=None,
                 buildername='html', confoverrides=None, status=None,
                 warning=None, freshenv=False, warningiserror=False, tags=None,
                 copy_srcdir_to_tmpdir=False, create_new_srcdir=False,
                 cleanup_on_errors=True, verbosity=0, parallel=0,
                 extensions='all'):
        """
        @param      srcdir                  source folder
        @param      outdir                  output folder
        @param      confdir                 configuration folder, default is srcdir
        @param      doctreedir              doc tree folder
        @param      buildername             HTML by default
        @param      confoverrides           None or dictionary
        @param      status                  StringIO to retrieve them
        @param      warning                 StringIO to retrieve them
        @param      freshenv                boolean
        @param      warningiserror          warning as errors?
        @param      tags                    additional documentation
        @param      copy_srcdir_to_tmpdir   copy the source to a temporary directory
        @param      create_new_srcdir       create a new source directory
        @param      cleanup_on_errors       force cleanup on errors
        @param      verbosity               integer
        @param      parallel                integer (number of threads)
        @param      extensions              if ``'all'``, add extensions implemented
                                            by this module, use ``None`` for an empty list,
                                            'extensions' must not be in *confoverrides*
        """
        self.cleanup_trees = []
        self.cleanup_on_errors = cleanup_on_errors
        srcdir = os.path.abspath(srcdir)
        outdir = os.path.abspath(outdir)

        if confdir is None:
            confdir = srcdir
        else:
            confdir = os.path.abspath(confdir)

        if doctreedir is None:
            doctreedir = os.path.join(outdir, '_pyq', 'doctrees')
            if not os.path.exists(doctreedir):
                os.makedirs(doctreedir)

        if confoverrides is None:
            confoverrides = {}
        if status is None:
            status = StringIO()
        if warning is None:
            warning = StringIO()

        if buildername == "rst":
            from ..sphinxext.sphinx_rst_builder import RstBuilder
            module = RstBuilder.__module__
        elif buildername == "md":
            from ..sphinxext.sphinx_md_builder import MdBuilder
            module = MdBuilder.__module__
        elif buildername in ("latex", "elatex", "pdf"):
            from ..sphinxext.sphinx_latex_builder import EnhancedLaTeXBuilder
            module = EnhancedLaTeXBuilder.__module__
        elif buildername == "doctree":
            from ..sphinxext.sphinx_doctree_builder import DocTreeBuilder
            module = DocTreeBuilder.__module__

        if 'extensions' not in confoverrides:
            if extensions == 'all':
                from ..sphinxext import get_default_extensions, get_default_standard_extensions
                exts = get_default_extensions(load_bokeh=False)
                exts += get_default_standard_extensions()
                skip = {'sphinx.ext.extlinks'}
                exts = [_ for _ in exts if _ not in skip]
                if buildername == "rst":
                    exts.insert(0, module)
            elif isinstance(extensions, list):
                exts = extensions
                if buildername == "rst":
                    exts = exts.copy()
                    exts.insert(0, module)
            elif buildername in ("rst", "md"):
                exts = [module]
            if exts is not None:
                confoverrides['extensions'] = exts

        # delayed import to speed up time
        with warnings.catch_warnings():
            warnings.simplefilter(
                "ignore", (DeprecationWarning, PendingDeprecationWarning))
            Sphinx.__init__(self, srcdir, confdir, outdir, doctreedir,
                            buildername, confoverrides, status,
                            warning, freshenv, warningiserror, tags,
                            verbosity, parallel)

        self._add_missing_element_in_config()

    def _add_missing_element_in_config(self):
        """
        Adds extra elements in config such as ``latex_elements``.
        """
        if not hasattr(self.config, "latex_elements"):
            self.config.latex_elements = {
                'papersize': 'a4',
                'pointsize': '10pt',
                'preamble': latex_preamble(),
            }

    def __str__(self):
        """
        usual
        """
        classname = self.__class__.__name__
        return '<%s buildername=%r>' % (classname, self.builder.name)

    def cleanup(self, error=None):
        """
        do some cleanup

        @param      error       error is an exception
        """
        from sphinx.theming import Theme

        if error and self.cleanup_on_errors is False:
            return

        Theme.themes.clear()
        for tree in self.cleanup_trees:
            shutil.rmtree(tree, True)
