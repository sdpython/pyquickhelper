"""
@file
@brief Various function to clean files.
"""
from __future__ import print_function
import os


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
    for root, _, files in os.walk("."):
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
