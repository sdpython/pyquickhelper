"""
@file
@brief Various function to clean files.

.. versionadded:: 0.9
"""

import os

def clean_exts(folder=".", fLOG=print, exts = [".pyd", ".so", ".o", ".def"] ):
    """
    clean files in a folder and subfolders with a given extensions

    @param      folder      folder to clean
    @param      fLOG        logging function
    @param      exts        extensions to clean
    @return                 list of removed files

    .. versionadded:: 0.9
    """
    rem = [ ]
    for root, dirs, files in os.walk("."):
        for f in files :
            ext = os.path.splitext(f)[-1]
            if ext in exts and "exe.win" not in root :
                filename = os.path.join(root,f)
                fLOG ("removing ", filename)
                os.remove(filename)
                rem.append(filename)
    return rem