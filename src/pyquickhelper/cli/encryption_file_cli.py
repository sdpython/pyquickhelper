"""
@file
@brief encrypt and decrypt command lines for just a file

.. versionadded:: 1.3
"""
import os
import argparse
import sys


def get_parser(encrypt):
    """
    defines the way to parse the magic command ``%encrypt`` and ``%decrypt``

    @param      encrypt     encrypt or decrypt
    @return                 parser
    """
    task = "encrypt" if encrypt else "decrypt"
    parser = argparse.ArgumentParser(
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
        raise FileNotFoundError(source)
    try:
        from pyquickhelper.filehelper import encrypt_stream, decrypt_stream
    except ImportError:
        folder = os.path.normpath(os.path.join(
            os.path.abspath(os.path.dirname(__file__)), "..", ".."))
        sys.path.append(folder)
        from pyquickhelper.filehelper import encrypt_stream, decrypt_stream

    if sys.version_info[0] >= 3 and isinstance(password, str):
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


def encrypt_file(fLOG=print):
    """
    encrypt using class @see fn encrypt_stream

    @param      fLOG        logging function
    """
    parser = get_parser(True)
    try:
        args = parser.parse_args()
    except SystemExit:
        print(parser.format_usage())
        args = None

    if args is not None:
        do_main(source=args.source, dest=args.dest,
                password=args.password, encrypt=True,
                fLOG=fLOG)


def decrypt_file(fLOG=print):
    """
    decrypt using class @see fn decrypt_stream

    @param      fLOG        logging function
    """
    parser = get_parser(False)
    try:
        args = parser.parse_args()
    except SystemExit:
        print(parser.format_usage())
        args = None

    if args is not None:
        do_main(source=args.source, dest=args.dest,
                password=args.password, encrypt=False,
                fLOG=fLOG)


if __name__ == "__main__":
    decrypt_file()
