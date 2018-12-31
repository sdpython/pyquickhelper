"""
@file
@brief Helpers for Internet
"""
import sys

try:
    import urllib.request as urllib_request
    from urllib.error import HTTPError
except ImportError:
    import urllib2 as urllib_request
    from urllib2 import HTTPError


class CannotDownloadException(Exception):
    """
    Raised by function @see fn get_url_content
    if something cannot be downloaded.
    """
    pass


def get_url_content(url, use_mozilla=False):
    """
    retrieve the content of an url
    @param      url             (str) url
    @param      use_mozilla     (bool) to use an header fill with Mozilla
    @return                     page
    """
    if use_mozilla:
        try:
            req = urllib_request.Request(
                url, headers={'User-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)' if sys.platform.startswith("win") else 'Mozilla/5.0'})
            u = urllib_request.urlopen(req)
        except HTTPError as e:
            raise CannotDownloadException(
                "Unable to download from url '{0}'".format(url)) from e
        text = u.read()
        u.close()
        text = text.decode("utf8")
        return text
    else:
        try:
            u = urllib_request.urlopen(url)
        except HTTPError as e:
            raise CannotDownloadException(
                "Unable to download from url '{0}'".format(url)) from e
        text = u.read()
        u.close()
        text = text.decode("utf8")
        return text
