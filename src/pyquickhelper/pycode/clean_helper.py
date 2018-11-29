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
    ``[".pyd", ".so", ".o", ".def"]``.

    .. versionchanged:: 1.8
        Parameter *fclean* was added.
    """
    if exts is None:
        exts = [".pyd", ".so", ".o", ".def"]
    rem = []
    for root, _, files in os.walk(folder):
        for f in files:
            ext = os.path.splitext(f)[-1]
            if ext in exts and "exe.win" not in root and "site-packages" not in root and \
               "_venv" not in root:
                filename = os.path.join(root, f)
                if fclean is not None and not fclean(filename):
                    continue
                fLOG("[clean_exts] removing ", filename)
                os.remove(filename)
                rem.append(filename)
    return rem


def clean_files(folder=".", posreg='.*', negreg=None, fLOG=print):
    """
    Cleans ``\\r`` in files a folder and subfolders with a given extensions.

    @param      folder      folder to clean
    @param      posreg      regular expression to select files to process
    @param      negreg      regular expression to skip files to process
    @param      fLOG        logging function
    @return                 list of processed files

    .. versionadded:: 1.8
    """
    def clean_file(name):
        with open(name, "rb") as f:
            content = f.read()
        new_content = content.replace(b"\r\n", b"\n")
        if new_content != content:
            with open(name, "wb") as f:
                f.write(content)
            return True
        else:
            return False

    if posreg and isinstance(posreg, str):
        posreg = re.compile(posreg)
    if negreg and isinstance(negreg, str):
        negreg = re.compile(negreg)

    res = []
    for root, _, files in os.walk(folder):
        for f in files:
            if posreg is None or posreg.search(f):
                if negreg is None or not negreg.search(f):
                    full = os.path.join(root, f)
                    r = clean_file(full)
                    if r and fLOG:
                        fLOG("[clean_files] processed '{0}'".format(full))
                        res.append(full)
    return res
