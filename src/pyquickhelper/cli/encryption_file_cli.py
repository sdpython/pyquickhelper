"""
@file
@brief encrypt and decrypt command lines for just a file
"""
from __future__ import print_function
import os
import argparse
import sys


def get_parser(encrypt):
    """
    defines the way to parse the magic command ``%encrypt`` and ``%decrypt``

    @param      encrypt     encrypt or decrypt
    @return                 parser
    """
    task = "encrypt_file" if encrypt else "decrypt_file"
    parser = argparse.ArgumentParser(prog=task,
                                     description='%s a file' % task +
                                     '\ndoes not work well in Python 2.7 with pycryptodome')
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


def do_main(source, dest, password, encrypt, fLOG=None):
    """
    Encrypt or decrypt of a file

    @param      source      source of files to encrypt or decrypt
    @param      dest        destination
    @param      password    password
    @param      encrypt     boolean, True to encrypt
    @param      fLOG        logging function
    """
    if not os.path.exists(source):
        raise FileNotFoundError(source)  # pragma: no cover
    try:
        from pyquickhelper.filehelper import encrypt_stream, decrypt_stream
    except ImportError:  # pragma: no cover
        folder = os.path.normpath(os.path.join(
            os.path.abspath(os.path.dirname(__file__)), "..", ".."))
        sys.path.append(folder)
        from pyquickhelper.filehelper import encrypt_stream, decrypt_stream

    if isinstance(password, str):
        password = bytes(password, encoding="ascii")

    if encrypt:
        encrypt_stream(key=password,
                       filename=source,
                       out_filename=dest,
                       chunksize=os.stat(source).st_size * 2 + 1)
    else:
        decrypt_stream(key=password,
                       filename=source,
                       out_filename=dest,
                       chunksize=os.stat(source).st_size * 2 + 1)


def encrypt_file(fLOG=print, args=None):
    """
    Encrypts using class @see fn encrypt_stream.

    @param      fLOG        logging function
    @param      args        to overwrite ``sys.args``

    .. cmdref::
        :title: Encrypt a file
        :cmd: pyquickhelper.cli.encryption_file_cli:encrypt_file

        Encrypt a file from the command line.
    """
    parser = get_parser(True)
    if args is not None and args == ['--help']:
        fLOG(parser.format_help())  # pragma: no cover
    else:
        try:
            args = parser.parse_args()
        except SystemExit:  # pragma: no cover
            if fLOG:
                fLOG(parser.format_usage())
            args = None

        if args is not None:
            do_main(source=args.source, dest=args.dest,
                    password=args.password, encrypt=True,
                    fLOG=fLOG)


def decrypt_file(fLOG=print, args=None):
    """
    Decrypts using class @see fn decrypt_stream.

    @param      fLOG        logging function
    @param      args        to overwrite ``sys.args``

    .. cmdref::
        :title: Decrypt a file
        :cmd: pyquickhelper.cli.encryption_file_cli:decrypt_file

        Decrypt a file from the command line.
    """
    parser = get_parser(False)
    if args is not None and args == ['--help']:
        fLOG(parser.format_help())  # pragma: no cover
    else:
        try:
            args = parser.parse_args()
        except SystemExit:  # pragma: no cover
            if fLOG:
                fLOG(parser.format_usage())
            args = None

        if args is not None:
            do_main(source=args.source, dest=args.dest,
                    password=args.password, encrypt=False,
                    fLOG=fLOG)


if __name__ == "__main__":
    decrypt_file()  # pragma: no cover
