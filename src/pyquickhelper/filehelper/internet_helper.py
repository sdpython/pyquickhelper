"""
@file
@brief Gather functions about downloading from internet, ...
"""

import os
import sys
if sys.version_info[0] == 2:
    import urllib2 as urllib_request
else:
    import urllib.request as urllib_request
from ..loghelper.flog import noLOG, _get_file_url
from .fexceptions import FileException
from ..loghelper.flog import _first_more_recent


def download(url, path_download=".", outfile=None, fLOG=noLOG):
    """
    Download a file

    If url is an url, downloads the file and return the downloaded
    If it has already been downloaded, it is not downloaded again
    The function raises an exception if the url does not contain ``http://`` or ``https://`` or ``ftp://``.

    @param      url                 url
    @param      path_download       download the file here
    @param      outfile             see below
    @param      fLOG                logging function
    @return                         the filename

    If *outfile* is None, the function will give a relative name
    based on the last part of the url.
    If *outfile* is "", the function will remove every weird character.
    If *outfile* is not null, the function will use it. It will be relative to
    the current folder and not *path_download*.

    .. versionadded:: 0.9

    """
    lurl = url.lower()
    if "http://" in lurl or "https://" in lurl or "ftp://":
        if outfile is None:
            dest = os.path.join(path_download, os.path.split(url)[-1])
        elif outfile == "":
            dest = _get_file_url(url, path_download)
        else:
            dest = outfile

        down = False
        nyet = dest + ".notyet"

        if os.path.exists(dest) and not os.path.exists(nyet):
            try:
                f1 = urllib_request.urlopen(url)
                down = _first_more_recent(f1, dest)
                newdate = down
                f1.close()
            except IOError as e:
                raise FileException("unable to access url: " + url) from e
        else:
            down = True
            newdate = False

        if down:
            if newdate:
                fLOG(" downloading (updated) ", url)
            else:
                fLOG(" downloading ", url)

            if len(url) > 4 and \
               url[-4].lower() in [".txt", ".csv", ".tsv", ".log"]:
                fLOG("creating text file ", dest)
                format = "w"
            else:
                fLOG("creating binary file ", dest)
                format = "wb"

            if os.path.exists(nyet):
                size = os.stat(dest).st_size
                fLOG("resume downloading (stop at", size, ") from ", url)
                request = urllib_request.Request(url)
                request.add_header("Range", "bytes=%d-" % size)
                fu = urllib_request.urlopen(request)
                f = open(dest, format.replace("w", "a"))
            else:
                fLOG("downloading ", url)
                request = urllib_request.Request(url)
                fu = urllib_request.urlopen(url)
                f = open(dest, format)

            open(nyet, "w").close()
            c = fu.read(2 ** 21)
            size = 0
            while len(c) > 0:
                size += len(c)
                fLOG("    size", size)
                f.write(c)
                f.flush()
                c = fu.read(2 ** 21)
            fLOG("end downloading")
            f.close()
            fu.close()
            os.remove(nyet)

        url = dest
        return url
    else:
        raise FileException("This url does not seem to be one: " + url)


def read_url(url, encoding=None):
    """
    read the content of a url

    @param      url         url
    @param      encoding    if None, the result type is bytes, str otherwise
    @return                 str or bytes

    .. versionadded:: 1.1
    """
    request = urllib_request.Request(url)
    if sys.version_info[0] == 2:
        fu = urllib_request.urlopen(request)
        content = fu.read()
        fu.close()
    else:
        with urllib_request.urlopen(request) as fu:
            content = fu.read()

    if encoding is None:
        return content
    else:
        return content.decode(encoding=encoding)
