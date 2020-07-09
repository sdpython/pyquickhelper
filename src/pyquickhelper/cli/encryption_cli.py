"""
@file
@brief encrypt and decrypt command lines
"""
from __future__ import print_function
import os
import argparse
import sys


def get_parser(encrypt):  # pylint: disable=W0621
    """
    Defines the way to parse the magic command ``%encrypt`` and ``%decrypt``.

    @param      encrypt     encrypt or decrypt
    @return                 parser
    """
    task = "encrypt" if encrypt else "decrypt"
    parser = argparse.ArgumentParser(prog=task,
                                     description='%s a folder.' % task +
                                     '\nFor a second run, the program looks into file status' +
                                     '\nto avoid crypting same file gain, it does only modified files' +
                                     '\nit does not work well in Python 2.7 with pycryptodome.')
    parser.add_argument(
        'source',
        help='folder to %s' % task)
    parser.add_argument(
        'dest',
        help='location of the %sed files' % task)
    parser.add_argument(
        'password',
        help='password, usually an ascii string with 16x characters')
    if encrypt:
        parser.add_argument(
            '-s',
            '--status',
            default="crypt_status.txt",
            help='to keep track of what was done')
        parser.add_argument(
            '-m',
            '--map',
            default="crypt_map.txt",
            help='mapping between raw files and crypted files')
    else:
        parser.add_argument(
            '-r',
            '--regex',
            default="",
            help='the script can retrieve only a subpart of the data defined by a regular expression')

    return parser


def do_main(source, dest, password, encrypt,  # pylint: disable=W0621
            crypt_file, crypt_map, regex=None, fLOG=None):
    """
    Encrypts or decrypts a folder, see @see cl EncryptedBackup.
    The function relies on module :epkg:`pycrypto`, :epkg:`cryptography`,
    algoritm `AES <https://fr.wikipedia.org/wiki/Advanced_Encryption_Standard>`_,
    `Fernet <http://cryptography.readthedocs.org/en/latest/fernet/>`_.

    @param      source      source of files to encrypt or decrypt
    @param      dest        destination
    @param      password    password
    @param      encrypt     boolean, True to encrypt
    @param      crypt_file  encrypted file
    @param      crypt_map   @see cl EncryptedBackup
    @param      regex       regular expression to filter in files to retrieve
    @param      fLOG        logging function
    """
    if not os.path.exists(source):
        raise FileNotFoundError(source)  # pragma: no cover
    try:
        from pyquickhelper.filehelper import EncryptedBackup, TransferAPIFile, FileTreeNode
    except ImportError:  # pragma: no cover
        folder = os.path.normpath(os.path.join(
            os.path.abspath(os.path.dirname(__file__)), "..", ".."))
        sys.path.append(folder)
        from pyquickhelper.filehelper import EncryptedBackup, TransferAPIFile, FileTreeNode

    if isinstance(password, str):
        password = bytes(password, encoding="ascii")

    root = source
    local = root
    api = TransferAPIFile(dest)

    if encrypt:
        if fLOG:
            fLOG("looking for file in", root)
        ft = FileTreeNode(root, repository=False, fLOG=fLOG, log1=True)
        enc = EncryptedBackup(key=password, file_tree_node=ft,
                              transfer_api=api, root_local=local, file_status=crypt_file,
                              file_map=crypt_map, fLOG=fLOG)

        if fLOG:
            fLOG("start backup")
        issue = enc.start_transfering()[1]

        for file, exc in issue:
            if fLOG:  # pragma: no cover
                fLOG("{0} -- {1}".format(file, exc))
    else:
        enc = EncryptedBackup(key=password, file_tree_node=None,
                              transfer_api=api, root_local=None, file_status=None,
                              file_map=None, fLOG=fLOG)
        if fLOG:
            fLOG("start restoration")
        enc.retrieve_all(source, regex=regex)


def encrypt(fLOG=print, args=None):
    """
    Encrypts using class @see cl EncryptedBackup.
    The function relies on module :epkg:`pycrypto`, :epkg:`cryptography`,
    algoritm `AES <https://fr.wikipedia.org/wiki/Advanced_Encryption_Standard>`_,
    `Fernet <http://cryptography.readthedocs.org/en/latest/fernet/>`_.

    @param      fLOG        logging function
    @param      args        to overwrite ``sys.args``

    .. cmdref::
        :title: Encrypt a string
        :cmd: pyquickhelper.cli.encryption_cli:encrypt

        Encrypts a string from the command line.
    """
    parser = get_parser(True)
    if args is not None and args == ['--help']:
        fLOG(parser.format_help())
    else:
        try:
            args = parser.parse_args(args=args)
        except SystemExit:  # pragma: no cover
            if fLOG:
                fLOG(parser.format_usage())
            args = None

        if args is not None:
            do_main(source=args.source, dest=args.dest, password=args.password,
                    encrypt=True, crypt_file=args.status, crypt_map=args.map, fLOG=fLOG)


def decrypt(fLOG=print, args=None):
    """
    Decrypts using class @see cl EncryptedBackup.
    The function relies on module :epkg:`pycrypto`, :epkg:`cryptography`,
    algoritm `AES <https://fr.wikipedia.org/wiki/Advanced_Encryption_Standard>`_,
    `Fernet <http://cryptography.readthedocs.org/en/latest/fernet/>`_.

    @param      fLOG        logging function
    @param      args        to overwrite ``sys.args``

    .. cmdref::
        :title: Decrypt a string
        :cmd: pyquickhelper.cli.encryption_cli:decrypt

        Decrypts an encrypted string from the command line.
    """
    parser = get_parser(False)
    if args is not None and args == ['--help']:
        fLOG(parser.format_help())
    else:
        try:
            args = parser.parse_args(args=args)
        except SystemExit:  # pragma: no cover
            if fLOG:
                fLOG(parser.format_usage())
            args = None

        if args is not None:
            do_main(source=args.dest, dest=args.source, password=args.password,
                    encrypt=False, crypt_file=None, crypt_map=None,
                    regex=args.regex if args.regex else None,
                    fLOG=fLOG)


if __name__ == "__main__":
    decrypt()  # pragma: no cover
