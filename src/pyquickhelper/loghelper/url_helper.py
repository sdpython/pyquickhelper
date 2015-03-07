"""
@file
@brief Helpers for Internet
"""

try:
    import urllib.request as urllib_request
except ImportError:
    import urllib2 as urllib_request


def get_url_content(url, use_mozilla=False):
    """
    retrieve the content of an url
    @param      url             (str) url
    @param      use_mozilla     (bool) to use an header fill with Mozilla
    @return                     page
    """
    if use_mozilla:
        req = urllib_request.Request(
            url, headers={'User-agent': 'Mozilla/5.0'})
        u = urllib_request.urlopen(req)
        text = u.read()
        u.close()
        text = text.decode("utf8")
        return text
    else:
        u = urllib_request.urlopen(url)
        text = u.read()
        u.close()
        text = text.decode("utf8")
        return text
