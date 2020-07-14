# -*- coding: utf-8 -*-
"""
@file
@brief Magic command to handle files
"""
import os
from IPython.core.magic import magics_class, line_magic

from .magic_class import MagicClassWithHelpers
from .magic_parser import MagicCommandParser
from ..filehelper import zip_files, gzip_files, zip7_files


@magics_class
class MagicCompress(MagicClassWithHelpers):

    """
    Defines magic commands to compress files.
    """

    @staticmethod
    def compress_parser():
        """
        defines the way to parse the magic command ``%compress``
        """
        parser = MagicCommandParser(prog="compress",
                                    description='display the content of a repository (GIT or SVN)')
        parser.add_argument(
            'dest',
            type=str,
            help='destination, the extension defines the compression format, zip, gzip 7z')
        parser.add_argument(
            'files',
            type=str,
            nargs="?",
            help='files to compress or a python list')
        return parser

    @line_magic
    def compress(self, line):
        """
        .. nbref::
            :title: %compress

            It compresses a list of files,
            it returns the number of compressed files::

                from pyquickhelper import zip_files, gzip_files, zip7_files
                if format == "zip":
                    zip_files(dest, files)
                elif format == "gzip":
                    gzip_files(dest, files)
                elif format == "7z":
                    zip7_files(dest, files)
                else:
                    raise ValueError("unexpected format: " + format)
        """
        parser = self.get_parser(MagicCompress.compress_parser, "compress")
        args = self.get_args(line, parser)

        if args is not None:
            dest = args.dest
            files = args.files
            format = os.path.splitext(dest)[-1].strip(".").lower()

            if format == "zip":
                return zip_files(dest, files)
            if format == "gzip":
                return gzip_files(dest, files)
            if format == "7z":
                return zip7_files(dest, files)
            raise ValueError(
                "Unexpected format: '{0}' from file '{1}'?".format(
                    format, dest))
        return None


def register_file_magics(ip=None):  # pragma: no cover
    """
    Registers magics function, can be called from a notebook.

    @param      ip      from ``get_ipython()``
    """
    if ip is None:
        from IPython import get_ipython
        ip = get_ipython()
    ip.register_magics(MagicCompress)
