"""
@file
@brief      Various helpers about files
"""

import os
import io
import stat
import sys
import warnings
from .synchelper import explore_folder_iterfile
from .internet_helper import read_url

if sys.version_info[0] == 2:
    from codecs import open    


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


def read_content_ufs(file_url_stream, encoding="utf8"):
    """
    read the content of a source, whether it is a url, a file, a stream
    or a string (in that case, it returns the string itself),
    we assume the content type is text

    @param      file_url_stream     file or url or stream or string
    @param      encoding            encoding
    @return                         content of the source (str)
    """
    if isinstance(file_url_stream, str  # unicode#
                  ):
        if os.path.exists(file_url_stream):
            with open(file_url_stream, "r", encoding=encoding) as f:
                return f.read()
        elif file_url_stream.startswith("http"):
            return read_url(file_url_stream, encoding=encoding)
        else:
            return file_url_stream
    elif isinstance(file_url_stream, io.StringIO):
        return file_url_stream.getvalue()
    elif isinstance(file_url_stream, io.BytesIO):
        return file_url_stream.getvalue().decode(encoding=encoding)
    else:
        raise TypeError(
            "unexpected type for file_url_stream: {0}".format(type(file_url_stream)))
