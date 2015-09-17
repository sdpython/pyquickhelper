"""
@file
@brief A function to download the content of a url.

.. versionadded:: 1.1
"""
import sys
import socket
import gzip
import warnings

if sys.version_info[0] == 2:
    import urllib2 as urllib_error
    import urllib2 as urllib_request
    import httplib as http_client

    class ConnectionResetError(Exception):

        """
        missing from Python 2.7
        """
        pass
else:
    import urllib.error as urllib_error
    import urllib.request as urllib_request
    import http.client as http_client


class InternetException(Exception):

    """
    Exception for the function @see fn get_url_content_timeout
    """
    pass


def get_url_content_timeout(url, timeout=10, output=None, encoding="utf8", raise_exception=True):
    """
    download a file from internet (we assume it is text information, otherwise, encoding should be None)

    @param      url                 (str) url
    @param      timeout             (int) in seconds, after this time, the function drops an returns None, -1 for forever
    @param      output              (str) if None, the content is stored in that file
    @param      encoding            (str) utf8 by default, but if it is None, the returned information is binary
    @param      raise_exception     (bool) True to raise an exception, False to send a warnings
    @return                         content of the url

    If the function automatically detects that the downloaded data is in gzip
    format, it will decompress it.

    The function raises the exception @see cl InternetException.

    .. versionadded:: 1.1
        It comes from `pyrsslocal <http://www.xavierdupre.fr/app/pyrsslocal/helpsphinx/index.html>`_.
    """
    try:
        if sys.version_info[0] == 2:
            if timeout != -1:
                raise NotImplementedError(
                    "for python 2.7, timeout cannot be -1")
            else:
                fu = urllib_request.urlopen(url)
                res = fu.read()
                fu.close()
        else:
            if timeout != -1:
                with urllib_request.urlopen(url, timeout=timeout) as ur:
                    res = ur.read()
            else:
                with urllib_request.urlopen(url) as ur:
                    res = ur.read()
    except (urllib_error.HTTPError, urllib_error.URLError) as e:
        if raise_exception:
            raise InternetException(
                "unable to retrieve content, url={0}".format(url)) from e
        warnings.warn(
            "unable to retrieve content from {0} exc: {1}".format(url, e))
        return None
    except socket.timeout as e:
        if raise_exception:
            raise InternetException(
                "unable to retrieve content, url={0}".format(url)) from e
        warnings.warn("unable to retrieve content from {0} because of timeout {1}: {2}".format(
            url, timeout, e))
        return None
    except ConnectionResetError as e:
        if raise_exception:
            raise InternetException(
                "unable to retrieve content, url={0}".format(url)) from e
        warnings.warn(
            "unable to retrieve content from {0} because of ConnectionResetError: {1}".format(url, e))
        return None
    except http_client.BadStatusLine as e:
        if raise_exception:
            raise InternetException(
                "unable to retrieve content, url={0}".format(url)) from e
        warnings.warn(
            "unable to retrieve content from {0} because of http.client.BadStatusLine: {1}".format(url, e))
        return None
    except http_client.IncompleteRead as e:
        if raise_exception:
            raise InternetException(
                "unable to retrieve content url={0}".format(url)) from e
        warnings.warn(
            "unable to retrieve content from {0} because of http.client.IncompleteRead: {1}".format(url, e))
        return None
    except Exception as e:
        if raise_exception:
            raise InternetException(
                "unable to retrieve content, url={0}, exc={1}".format(url, e)) from e
        warnings.warn(
            "unable to retrieve content from {0} because of unknown exception: {1}".format(url, e))
        raise e

    if len(res) >= 2 and res[:2] == b"\x1f\x8B":
        # gzip format
        res = gzip.decompress(res)

    if encoding is not None:
        try:
            content = res.decode(encoding)
        except UnicodeDecodeError as e:
            # we try different encoding

            laste = [e]
            othenc = ["iso-8859-1", "latin-1"]

            for encode in othenc:
                try:
                    content = res.decode(encode)
                    break
                except UnicodeDecodeError as e:
                    laste.append(e)
                    content = None

            if content is None:
                mes = ["unable to parse blog post: " + url]
                mes.append("tried:" + str([encoding] + othenc))
                mes.append("beginning:\n" + str([res])[:50])
                for e in laste:
                    mes.append("Exception: " + str(e))
                raise ValueError("\n".join(mes))
    else:
        content = res

    if output is not None:
        if encoding is not None:
            with open(output, "w", encoding=encoding) as f:
                f.write(content)
        else:
            with open(output, "wb") as f:
                f.write(content)

    return content
