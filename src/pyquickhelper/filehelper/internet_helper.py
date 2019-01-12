"""
@file
@brief Gather functions about downloading from internet, ...
"""
import os
import sys
import shutil
import urllib.request as urllib_request
import urllib.error as urllib_error
from ..loghelper.flog import noLOG, _get_file_url
from .fexceptions import FileException
from ..loghelper.flog import _first_more_recent


class ReadUrlException(Exception):
    """
    Raised by @see fn read_url.
    """
    pass


def download(url, path_download=".", outfile=None, fLOG=noLOG):
    """
    Downloads a small file.
    If *url* is an url, it downloads the file and returns the downloaded filename.
    If it has already been downloaded, it is not downloaded again
    The function raises an exception if the url does not contain
    ``http://`` or ``https://`` or ``ftp://``.

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
    """
    lurl = url.lower()
    if lurl.startswith("file://"):
        if outfile is None:
            last = os.path.split(url)[-1]
            if last.startswith("__cached__"):
                last = last[len("__cached__"):]
            dest = os.path.join(path_download, last)
        elif outfile == "":
            dest = _get_file_url(url, path_download)
        else:
            dest = outfile

        src = url[7:].lstrip(
            "/") if sys.platform.startswith("win") else url[7:]
        shutil.copy(src, dest)
        return dest
    elif "http://" in lurl or "https://" in lurl or "ftp://":
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
            except urllib_error.HTTPError as e:
                raise ReadUrlException(
                    "Unable to fetch '{0}'".format(url)) from e
            except IOError as e:
                raise ReadUrlException(
                    "Unable to download '{0}'".format(url)) from e
        else:
            down = True
            newdate = False

        if down:
            if newdate:
                fLOG("[download] downloading (updated) ", url)
            else:
                fLOG("[download] downloading ", url)

            if len(url) > 4 and \
               url[-4].lower() in [".txt", ".csv", ".tsv", ".log"]:
                fLOG("creating text file ", dest)
                format = "w"
            else:
                fLOG("creating binary file ", dest)
                format = "wb"

            if os.path.exists(nyet):
                size = os.stat(dest).st_size
                fLOG("[download] resume downloading (stop at", size, ") from ", url)
                try:
                    request = urllib_request.Request(url)
                    request.add_header("Range", "bytes=%d-" % size)
                    fu = urllib_request.urlopen(request)
                except urllib_error.HTTPError as e:
                    raise ReadUrlException(
                        "Unable to fetch '{0}'".format(url)) from e
                f = open(dest, format.replace("w", "a")    # pylint: disable=W1501
                         )  # pylint: disable=W1501
            else:
                fLOG("[download] downloading ", url)
                try:
                    request = urllib_request.Request(url)
                    fu = urllib_request.urlopen(url)
                except urllib_error.HTTPError as e:
                    raise ReadUrlException(
                        "Unable to fetch '{0}'".format(url)) from e
                f = open(dest, format)

            open(nyet, "w").close()
            c = fu.read(2 ** 21)
            size = 0
            while len(c) > 0:
                size += len(c)
                fLOG("[download]    size", size)
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
    Reads the content of a url.

    @param      url         url
    @param      encoding    if None, the result type is bytes, str otherwise
    @return                 str (encoding is not None) or bytes
    """
    request = urllib_request.Request(url)
    try:
        with urllib_request.urlopen(request) as fu:
            content = fu.read()
    except Exception as e:
        import urllib.parse as urlparse
        res = urlparse.urlparse(url)
        raise ReadUrlException(
            "unable to open url '{0}' scheme: {1}\nexc: {2}".format(url, res, e))

    if encoding is None:
        return content
    else:
        return content.decode(encoding=encoding)
