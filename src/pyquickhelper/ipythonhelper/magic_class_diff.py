# -*- coding: utf-8 -*-
"""
@file
@brief Magic command to handle files
"""
from IPython.core.magic import magics_class, line_magic
from IPython.core.display import display_html

from .magic_class import MagicClassWithHelpers
from .magic_parser import MagicCommandParser
from ..filehelper import create_visual_diff_through_html_files


@magics_class
class MagicDiff(MagicClassWithHelpers):

    """
    Defines magic commands to visualize differences between files.
    """

    @staticmethod
    def textdiff_parser():
        """
        defines the way to parse the magic command ``%textdiff``
        """
        parser = MagicCommandParser(prog="textdiff",
                                    description='show the differences between two files, two text')
        parser.add_argument('f1', type=str, help='first file or text or url')
        parser.add_argument('f2', type=str, help='second file or text or url')
        parser.add_argument(
            '-c',
            '--context',
            default="",
            help='context view, empty to see everything, > 0 to see only a couple of lines around the changes')
        parser.add_argument(
            '-i',
            '--inline',
            action="store_true",
            default=False,
            help='True=one column (inline) or False=two columns')
        parser.add_argument(
            '-e',
            '--encoding',
            default="utf8",
            help='file encoding')
        return parser

    @line_magic
    def textdiff(self, line):
        """
        .. nbref::
            :title: %textdiff
            :tag: nb

            It displays differences between two text files, two strings, two urls,
            it is based on :func:`create_visual_diff_through_html_files
            <pyquickhelper.filehelper.visual_sync.create_visual_diff_through_html_files>`.
            Check blog post :ref:`Visualize differences between two files in a notebook <b-diffview>`
            to see an example. See also
            `A magic command to visualize differences between two files in a notebook
            <http://www.xavierdupre.fr/app/pyensae/helpsphinx/blog/2015/2015-04-23_textdiff.html>`_.
            The magic command is equivalent to::

                from IPython.core.display import display_html, display_javascript
                from pyquickhelper import docstring2html, create_visual_diff_through_html_files
                html, js = create_visual_diff_through_html_files(<f1>, <f2>,
                                encoding=<encoding>, notebook=True,
                                context_size=None if <context> in [None, ""] else int(<context>),
                                inline_view=<inline>)
                display_html(html)
                display_javascript(js)

        """
        parser = self.get_parser(MagicDiff.textdiff_parser, "textdiff")
        args = self.get_args(line, parser)

        if args is not None:
            html, js = create_visual_diff_through_html_files(args.f1, args.f2, encoding=args.encoding, notebook=True,
                                                             context_size=None if args.context in [
                                                                 None, ""] else int(args.context),
                                                             inline_view=args.inline)
            display_html(html)
            return js
        return None

    @line_magic
    def difftext(self, line):
        """
        Defines ``%difftext`` which calls @see me textdiff.
        but should be easier to remember
        """
        return self.textdiff(line)


def register_file_magics(ip=None):  # pragma: no cover
    """
    Register magics function, can be called from a notebook.

    @param      ip      from ``get_ipython()``
    """
    if ip is None:
        from IPython import get_ipython
        ip = get_ipython()
    ip.register_magics(MagicDiff)
