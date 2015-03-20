"""
@file
@brief      Various helpers about files
"""

import os
import stat
from .synchelper import explore_folder_iterfile


def change_file_status(folder, status=stat.S_IWRITE, strict=False):
    """
    change the status of all files inside a folder

    @param      folder      folder
    @param      status      new status
    @param      strict      False, use ``|=``, True, use ``=``
    @return                 list of modified files
    """
    res = []
    if strict:
        for f in explore_folder_iterfile(temp):
            mode = os.stat(f).st_mode
            nmode = status
            if nmode != mode:
                os.chmod(f, nmode)
                res.append(f)
    else:
        for f in explore_folder_iterfile(folder):
            mode = os.stat(f).st_mode
            nmode = mode | stat.S_IWRITE
            if nmode != mode:
                os.chmod(f, nmode)
                res.append(f)
    return res
