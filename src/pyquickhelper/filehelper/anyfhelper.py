"""
@file
@brief      Various helpers about files
"""
import os
import stat
import warnings
from io import BytesIO, StringIO
from .synchelper import explore_folder_iterfile
from .internet_helper import read_url
from .file_info import is_file_string, is_url_string


def change_file_status(folder, status=stat.S_IWRITE, strict=False,
                       include_folder=True):
    """
    Changes the status of all files inside a folder.

    @param      folder          folder or file
    @param      status          new status
    @param      strict          False, use ``|=``, True, use ``=``
    @param      include_folder  change the status of the folders as well
    @return                     list of modified files

    By default, status is ``stat.S_IWRITE``.
    If *folder* is a file, the function changes the status of this file,
    otherwise, it will change the status of every file the folder contains.
    """
    if os.path.isfile(folder):
        if include_folder:
            dirname = os.path.dirname(folder)
            todo = [dirname, folder]
        else:
            todo = [folder]
        res = []

        for f in todo:
            mode = os.stat(f).st_mode
            if strict:
                nmode = status
                if nmode != mode:
                    os.chmod(f, nmode)
                    res.append(f)
            else:
                nmode = mode | stat.S_IWRITE
                if nmode != mode:
                    os.chmod(f, nmode)
                    res.append(f)
        return res
    else:
        res = []
        dirname = set()
        if strict:
            for f in explore_folder_iterfile(folder):
                if include_folder:
                    d = os.path.dirname(f)
                    if d not in dirname:
                        dirname.add(d)
                        mode = os.stat(d).st_mode
                        nmode = status
                        if nmode != mode:
                            os.chmod(d, nmode)
                            res.append(d)
                try:
                    mode = os.stat(f).st_mode
                except FileNotFoundError:
                    # It appends for some weird path.
                    warnings.warn(
                        "[change_file_status] unable to find '{0}'".format(f), UserWarning)
                    continue
                nmode = status
                if nmode != mode:
                    os.chmod(f, nmode)
                    res.append(f)

            # It ends up with the folder.
            if include_folder:
                d = folder
                if d not in dirname:
                    mode = os.stat(d).st_mode
                    nmode = status
                    if nmode != mode:
                        os.chmod(d, nmode)
                        res.append(d)
        else:
            for f in explore_folder_iterfile(folder):
                if include_folder:
                    d = os.path.dirname(f)
                    if d not in dirname:
                        dirname.add(d)
                        mode = os.stat(d).st_mode
                        nmode = mode | stat.S_IWRITE
                        if nmode != mode:
                            os.chmod(d, nmode)
                            res.append(d)
                try:
                    mode = os.stat(f).st_mode
                except FileNotFoundError:
                    # it appends for some weird path
                    warnings.warn(
                        "[change_file_status] unable to find '{0}'".format(f), UserWarning)
                    continue
                nmode = mode | stat.S_IWRITE
                if nmode != mode:
                    os.chmod(f, nmode)
                    res.append(f)

            # It ends up with the folder.
            if include_folder:
                d = folder
                if d not in dirname:
                    mode = os.stat(d).st_mode
                    nmode = mode | stat.S_IWRITE
                    if nmode != mode:
                        os.chmod(d, nmode)
                        res.append(d)
        return res


def read_content_ufs(file_url_stream, encoding="utf8", asbytes=False,
                     add_source=False, min_size=None):
    """
    Reads the content of a source, whether it is a url, a file, a stream
    or a string (in that case, it returns the string itself),
    it assumes the content type is text.

    @param      file_url_stream     file or url or stream or string
    @param      encoding            encoding
    @param      asbytes             return bytes instead of chars
    @param      add_source          also return the way the content was obtained
    @param      min_size            if not empty, the function raises an exception
                                    if the size is below that theshold
    @return                         content of the source (str) or *(content, type)*

    Type can be:

    * *rb*: binary file
    * *r*: text file
    * *u*: url
    * *ub*: binary content from url
    * *s*: string
    * *b*: binary string
    * *S*: StringIO
    * *SB*: BytesIO
    * *SBb*: BytesIO, return bytes

    The function can return bytes.
    """
    def check_size(cont):
        if min_size is not None and len(cont) < min_size:
            raise RuntimeError(
                "File '{}' is smaller than {}.".format(
                    file_url_stream, min_size))

    if isinstance(file_url_stream, str):
        if is_file_string(file_url_stream) and os.path.exists(file_url_stream):
            if asbytes:
                with open(file_url_stream, "rb") as f:
                    content = f.read()
                    check_size(content)
                    return (content, "rb") if add_source else content
            with open(file_url_stream, "r", encoding=encoding) as f:
                content = f.read()
                check_size(content)
                return (content, "r") if add_source else content
        if len(file_url_stream) < 5000 and file_url_stream.startswith("http"):
            content = read_url(file_url_stream, encoding=encoding)
            check_size(content)
            return (content, "u") if add_source else content
        if is_url_string(file_url_stream):
            if asbytes:
                content = read_url(file_url_stream)
                check_size(content)
                return (content, "ub") if add_source else content
            if encoding is None:
                raise ValueError(
                    "cannot return bytes if encoding is None for url: " + file_url_stream)
            content = read_url(file_url_stream, encoding=encoding)
            check_size(content)
            return (content, "u") if add_source else content
        # the string should the content itself
        if isinstance(file_url_stream, str):
            if asbytes:
                raise TypeError(
                    "file_url_stream is str when expected bytes")
            return (file_url_stream, "s") if add_source else file_url_stream
        if asbytes:
            return (file_url_stream, "b") if add_source else file_url_stream
        raise TypeError(
            "file_url_stream is bytes when expected str")

    if isinstance(file_url_stream, bytes):
        if asbytes:
            return (file_url_stream, "b") if add_source else file_url_stream
        content = file_url_stream.encode(encoding=encoding)
        check_size(content)
        return (content, "b") if add_source else content
    if isinstance(file_url_stream, StringIO):
        v = file_url_stream.getvalue()
        if asbytes and v:
            content = v.encode(encoding=encoding)
            check_size(content)
            return (content, "Sb") if add_source else content
        return (v, "S") if add_source else v
    if isinstance(file_url_stream, BytesIO):
        v = file_url_stream.getvalue()
        if asbytes or not v:
            return (v, "SBb") if add_source else v
        content = v.decode(encoding=encoding)
        check_size(content)
        return (content, "SB") if add_source else content
    raise TypeError(
        "unexpected type for file_url_stream: {0}\n{1}".format(
            type(file_url_stream), file_url_stream))
