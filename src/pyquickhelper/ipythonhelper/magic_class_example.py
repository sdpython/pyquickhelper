# -*- coding: utf-8 -*-
"""
@file
@brief Example of a class which defines magic commands.
"""
from __future__ import print_function
from IPython.core.magic import magics_class, line_magic
from .magic_class import MagicClassWithHelpers
from .magic_parser import MagicCommandParser
from ..helpgen import docstring2html


@magics_class
class MagicClassExample(MagicClassWithHelpers):

    """
    .. faqref::
        :title: Define a magic command

        This class is an example of how a magic commands can be defined
        with parameters as if it was a regular command in a terminal.
        The class @see cl MagicClassExample defines magic
        command ``htmlhelp`` and the associated parser.
        Function @see fn load_ipython_extension
        register the magic command through ``%load_ext pyquickhelper``.
        The magic command can be unit tested with::

            mg = MagicClassExample()
            mg.add_context(context={"MagicClassExample": MagicClassExample})
            cmd = "MagicClassExample -f text"
            res = mg.htmlhelp(cmd)
            assert "NB(example of a magic command)"
    """

    @staticmethod
    def htmlhelp_parser():
        """
        Defines the way to parse the magic command ``%htmlhelp``.
        """
        parser = MagicCommandParser(prog="htmlhelp",
                                    description='display help for an object in HTML format')
        parser.add_argument(
            'obj',
            type=str,
            help='a python object')
        parser.add_argument(
            '-f',
            '--format',
            type=str,
            default="html",
            help='format',
            choices=['text', 'html', 'rst', 'rawhtml'])
        parser.add_argument(
            '-np',
            '--no-print',
            action='store_true',
            help='by default, the magic command outputs everything on the standard output, '
                 'if specified, it returns a string')
        return parser

    @line_magic
    def htmlhelp(self, line):
        """
        Defines ``%htmlhelp``, it displays the help for an object in :epkg:`HTML`.

        .. nbref::
            :title: %htmlhelp

            Magic command ``htmlhelp`` convert docstring (RST)
            into HTML format for a better display in a notebook.
            It is equivalent to the code:

            ::

                from pyquickhelper.helpgen import docstring2html
                obj = <function or object>
                docstring2html(obj, format="html")

            See function @see fn docstring2html.
        """
        parser = self.get_parser(MagicClassExample.htmlhelp_parser, "htmlhelp")
        args = self.get_args(line, parser)

        if args is not None:
            obj = args.obj
            format = args.format
            nop = args.no_print
            if nop or format == "html":
                return docstring2html(obj, format=format)
            print(docstring2html(obj, format=format))
        return None


def register_file_magics(ip=None):  # pragma: no cover
    """
    Registers magics functions, can be called from a notebook.

    @param      ip      from ``get_ipython()``
    """
    if ip is None:
        from IPython import get_ipython
        ip = get_ipython()
    ip.register_magics(MagicClassExample)
