"""
@file
@brief Various function to clean files.
"""
from __future__ import print_function
import os
import re


def clean_exts(folder=".", fLOG=print, exts=None, fclean=None):
    """
    Cleans files in a folder and subfolders with a given extensions.

    @param      folder      folder to clean
    @param      fLOG        logging function
    @param      exts        extensions to clean
    @param      fclean      if not None, ``fclean(name) -> True`` to clean
    @return                 list of removed files

    If *exts* is None, it will be replaced by
    ``{".pyd", ".so", ".o", ".def", ".obj"}``.

    .. versionchanged:: 1.8
        Parameter *fclean* was added.
    """
    if exts is None:
        exts = {".pyd", ".so", ".o", ".def", ".obj"}
    rem = []
    for root, _, files in os.walk(folder):
        for f in files:
            ext = os.path.splitext(f)[-1]
            if (ext in exts and "exe.win" not in root and "site-packages" not in root and
                    "_venv" not in root):  # pragma: no cover
                filename = os.path.join(root, f)
                if fclean is not None and not fclean(filename):
                    continue
                fLOG("[clean_exts] removing ", filename)
                os.remove(filename)
                rem.append(filename)
    return rem


def clean_files(folder=".", posreg='.*[.]((py)|(rst))$',
                negreg=".*[.]git/.*", op="CR", fLOG=print):
    """
    Cleans ``\\r`` in files a folder and subfolders with a given extensions.
    Backslashes are replaces by ``/``. The regular expressions
    applies on the relative path starting from *folder*.

    :param folder: folder to clean
    :param posreg: regular expression to select files to process
    :param negreg: regular expression to skip files to process
    :param op: kind of cleaning to do, see below for the available option
    :param fLOG: logging function
    :return: list of processed files

    The following cleaning are available:

    * ``'CR'``: replaces ``'\\r\\n'`` by ``'\\n'``
    * ``'pep8'``: applies :epkg:`pep8` convention
    """
    def clean_file_cr(name):
        with open(name, "rb") as f:
            content = f.read()
        new_content = content.replace(b"\r\n", b"\n")
        if new_content != content:
            with open(name, "wb") as f:
                f.write(new_content)
            return True
        else:
            return False

    if op == 'CR':
        clean_file = clean_file_cr
    elif op == 'pep8':
        from .code_helper import remove_extra_spaces_and_pep8
        clean_file = remove_extra_spaces_and_pep8
    else:
        raise ValueError("Unknown cleaning '{0}'.".format(op))

    if posreg and isinstance(posreg, str):
        posreg = re.compile(posreg)
    if negreg and isinstance(negreg, str):
        negreg = re.compile(negreg)

    res = []
    for root, _, files in os.walk(folder):
        for f in files:
            full = os.path.join(root, f)
            rel = os.path.relpath(full, folder)
            fn = rel.replace("\\", "/")
            if posreg is None or posreg.search(fn):
                if negreg is None or not negreg.search(fn):
                    r = clean_file(full)
                    if r and fLOG:
                        fLOG("[clean_files] processed '{0}'".format(fn))
                        res.append(rel)
    return res
