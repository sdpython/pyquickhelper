"""
@file
@brief      Various helpers about files
"""

import os
import stat
import warnings
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
        for f in explore_folder_iterfile(folder):
            try:
                mode = os.stat(f).st_mode
            except FileNotFoundError:
                # it appends for some weird path
                # GitHub\pyensae\src\pyensae\file_helper\pigjar\pig-0.14.0\contrib\piggybank\java\build\classes\org\apache\pig\piggybank\storage\IndexedStorage$IndexedStorageInputFormat$IndexedStorageRecordReader$IndexedStorageRecordReaderComparator.class
                warnings.warn("[change_file_status] unable to find " + f)
                continue
            nmode = status
            if nmode != mode:
                os.chmod(f, nmode)
                res.append(f)
    else:
        for f in explore_folder_iterfile(folder):
            try:
                mode = os.stat(f).st_mode
            except FileNotFoundError:
                # it appends for some weird path
                warnings.warn("[change_file_status] unable to find " + f)
                continue
            nmode = mode | stat.S_IWRITE
            if nmode != mode:
                os.chmod(f, nmode)
                res.append(f)
    return res
