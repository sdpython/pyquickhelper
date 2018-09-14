# -*- coding: utf-8 -*-
"""
@file
@brief Inspired from module
`sphinx-testing <https://github.com/sphinx-doc/sphinx-testing/>`_

.. versionadded:: 1.3
"""

import shutil
import os
import sys
from sphinx.application import Sphinx


if sys.version_info[0] == 2:
    from StringIO import StringIO
else:
    from io import StringIO


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

        .. versionchanged:: 1.6
            Parameter *extensions* was added.
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

        if 'extensions' not in confoverrides:
            if extensions == 'all':
                from ..sphinxext import get_default_extensions, get_default_standard_extensions
                exts = get_default_extensions() + get_default_standard_extensions()
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

        Sphinx.__init__(self, srcdir, confdir, outdir, doctreedir,
                        buildername, confoverrides, status,
                        warning, freshenv, warningiserror, tags,
                        verbosity, parallel)

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
        from sphinx.ext.autodoc import AutoDirective

        if error and self.cleanup_on_errors is False:
            return

        Theme.themes.clear()
        AutoDirective._registry.clear()
        for tree in self.cleanup_trees:
            shutil.rmtree(tree, True)
