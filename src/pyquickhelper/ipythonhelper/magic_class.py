# -*- coding: utf-8 -*-
"""
@file
@brief Magic command to handle files
"""
from __future__ import print_function
import warnings
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from IPython.core.magic import Magics, magics_class


@magics_class
class MagicClassWithHelpers(Magics):

    """
    Provides some functions reused in others classes inherited from *Magics*.
    The class should not be registered as it is but should be
    used as an ancestor for another class.
    It can be registered this way::

        def register_file_magics():
            from IPython import get_ipython
            ip = get_ipython()
            ip.register_magics(MagicFile)
    """

    _parser_store = {}

    @property
    def Context(self):
        """
        return the context or None
        """
        if self.shell is None:
            return None
        return self.shell.user_ns

    def add_context(self, context):
        """
        add context to the class, mostly for debug purpose

        @param      context     dictionary
        """
        if self.shell is None:
            class EmptyClass:

                def __init__(self):
                    self.user_ns = {}
            self.shell = EmptyClass()
        for k, v in context.items():
            self.shell.user_ns[k] = v

    def get_parser(self, parser_class, name):
        """
        Returns a parser for a magic command, initializes it
        if it does not exists, it creates it. The parsers are stored
        in static member *_parser_store*.

        @param      parser_class    the parser to use for this magic command
        @param      name            name of the static variable which will contain the parser

        See method @see me get_args
        """
        res = MagicClassWithHelpers._parser_store.get(name, None)
        if res is None:
            MagicClassWithHelpers._parser_store[name] = parser_class()
            return MagicClassWithHelpers._parser_store[name]
        return res

    def get_args(self, line, parser, print_function=print):
        """
        parser a command line with a given parser

        @param      line            string (command line)
        @param      parser          parser which has to be used to parse *line*
        @param      print_function  function to use to display the help
        @return                     results

        If the line cannot be parsed, the function displays the help
        using function print.

        Example::

            @line_magic
            def custom_magic_command(self, line):
                parser = self.get_parser(MagicClass.custom_magic_command_parser, "custom_magic_command")
                args = self.get_args(line, parser)
                if args is not None:
                    param = args.param

                    # ....
        """
        try:
            args = parser.parse_cmd(line, context=self.Context)
        except SystemExit:  # pragma: no cover
            print_function(parser.format_usage())
            args = None

        return args
