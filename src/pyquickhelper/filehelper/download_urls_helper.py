# -*- coding: utf-8 -*-
"""
@file
@brief Series of functions related to folder, explore, synchronize, remove (recursively).
"""
import re
from .synchelper import explore_folder_iterfile
from .download_helper import get_urls_content_timeout


def download_urls_in_folder_content(folder, pattern=".+[.]((py)|(ipynb))", neg_pattern=None,
                                    recursive=True, timeout=10, folder_dest=None,
                                    encoding='utf-8', raise_exception=False, chunk=None,
                                    fLOG=None):
    """
    Iterates on files in folder, parse them, extracts all urls, download
    them in a folder.

    :param folder: folder
    :param pattern: if None, get all files, otherwise, it is a regular expression,
        the filename must verify (with the folder is fullname is True)
    :param neg_pattern: negative pattern to exclude files
    :param fullname: if True, include the subfolder while checking the regex
    :param recursive: look into subfolders
    :param urls: urls
    :param timeout: in seconds, after this time, the function drops an returns None, -1 for forever
    :param folder_dest: if None, the content is stored in that file
    :param encoding: None by default, but if it is None, the returned information is binary
    :param raise_exception: True to raise an exception, False to send a warnings
    :param chunk: save data every chunk (only if output is not None)
    :param fLOG: logging function (only applies when chunk is not None)
    :return: list of downloaded content
    """
    if neg_pattern == '':
        neg_pattern = None  # pragma: no cover
    if chunk == '':
        chunk = None  # pragma: no cover
    if isinstance(chunk, str):
        chunk = int(chunk)  # pragma: no cover
    res = []
    url_pattern = ("(?i)\\b((?:[a-z][\\w-]+:(?:/{1,3}|[a-z0-9%])|www\\d{0,3}[.]|[a-z0-9.\\-]+"
                   "[.][a-z]{2,4}/)(?:[^\\s()<>]+|\\(([^\\s()<>]+|(\\([^\\s()<>]+\\)))*\\))+"
                   "(?:\\(([^\\s()<>]+|(\\([^\\s()<>]+\\)))*\\)|[^\\s`!()\\[\\]{};:"
                   "'\\\".,<>?]))")
    reg = re.compile(url_pattern)
    for obj in explore_folder_iterfile(folder, pattern=pattern, neg_pattern=neg_pattern,
                                       fullname=True, recursive=recursive):
        with open(obj, "r", encoding=encoding, errors='ignore') as f:
            content = f.read()
        fall = reg.findall(content)
        if len(fall) == 0:
            continue
        if fLOG is not None:
            fLOG("[download_urls_in_folder_content] explore '{}'".format(obj))
        urls = [f[0] for f in fall]
        r = get_urls_content_timeout(urls, folder=folder_dest, timeout=timeout,
                                     raise_exception=raise_exception, chunk=chunk,
                                     fLOG=fLOG)
        res.extend(r)
    return res
