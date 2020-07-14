# -*- coding: utf-8 -*-
"""
@file
@brief Magic command to handle files
"""
import os
from IPython.core.magic import magics_class, line_magic

from .magic_class import MagicClassWithHelpers
from .magic_parser import MagicCommandParser
from ..filehelper import encrypt_stream, decrypt_stream


@magics_class
class MagicCrypt(MagicClassWithHelpers):

    """
    Defines magic commands to encrypt and decrypt file.
    """

    @staticmethod
    def endecrypt_file_parser(encrypt):
        """
        defines the way to parse the magic command ``%encrypt_file`` and ``%decrypt_file``

        @param      encrypt     True to encrypt or False to decrypt
        @return                 parser
        """
        task = "encrypt" if encrypt else "decrypt"
        parser = MagicCommandParser(prog="%scrypt_file" % task[:2],
                                    description='%s a file' % task +
                                    '\ndoes not work well in Python 2.7 with pycryptodomex')
        parser.add_argument(
            'source',
            help='file to %s' % task)
        parser.add_argument(
            'dest',
            help='location of the %sed file' % task)
        parser.add_argument(
            'password',
            help='password, usually an ascii string with 16x characters')

        return parser

    @staticmethod
    def encrypt_file_parser():
        """
        defines the way to parse the magic command ``%encrypt_file``
        """
        return MagicCrypt.endecrypt_file_parser(True)

    @staticmethod
    def decrypt_file_parser():
        """
        defines the way to parse the magic command ``%decrypt_file``
        """
        return MagicCrypt.endecrypt_file_parser(False)

    @line_magic
    def encrypt_file(self, line):
        """
        .. nbref::
            :title: %encrypt_file
            :tag: nb
            :lid: l-nb-encrypt-file

            The magic command is equivalent to::

                from pyquickhelper.filehelper import encrypt_stream

                password = "password"
                source = "file source"
                dest = "file destination"

                if isinstance(password, str):
                    password = bytes(password, encoding="ascii")

                encrypt_stream(key=password, filename=source, out_filename=dest,
                               chunksize=os.stat(source).st_size * 2 + 1)
        """
        parser = self.get_parser(
            MagicCrypt.encrypt_file_parser, "encrypt_file")
        args = self.get_args(line, parser)

        if args is not None:
            password = args.password
            source = args.source
            dest = args.dest

            if isinstance(password, str):
                password = bytes(password, encoding="ascii")

            return encrypt_stream(key=password, filename=source, out_filename=dest,
                                  chunksize=os.stat(source).st_size * 2 + 1)
        return None

    @line_magic
    def decrypt_file(self, line):
        """
        .. nbref::
            :title: %decrypt_file

            The magic command is equivalent to::

                from pyquickhelper.filehelper import decrypt_stream

                password = "password"
                source = "file source"
                dest = "file destination"

                if isinstance(password, str):
                    password = bytes(password, encoding="ascii")

                decrypt_stream(key=password, filename=source, out_filename=dest,
                               chunksize=os.stat(source).st_size * 2 + 1)
        """
        parser = self.get_parser(
            MagicCrypt.decrypt_file_parser, "decrypt_file")
        args = self.get_args(line, parser)

        if args is not None:
            password = args.password
            source = args.source
            dest = args.dest

            if isinstance(password, str):
                password = bytes(password, encoding="ascii")

            return decrypt_stream(key=password, filename=source, out_filename=dest,
                                  chunksize=os.stat(source).st_size * 2 + 1)
        return None


def register_file_magics(ip=None):  # pragma: no cover
    """
    Register magics function, can be called from a notebook.

    @param      ip      from ``get_ipython()``
    """
    if ip is None:
        from IPython import get_ipython
        ip = get_ipython()
    ip.register_magics(MagicCrypt)
