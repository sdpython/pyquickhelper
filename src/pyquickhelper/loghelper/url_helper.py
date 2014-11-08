"""
@file
@brief Helpers for Internet
"""

import urllib.request

def get_url_content(url, use_mozilla = False):
    """
    retrieve the content of an url
    @param      url             (str) url
    @param      use_mozilla     (bool) to use an header fill with Mozilla
    @return                     page
    """
    if use_mozilla :
        req = urllib.request.Request(url, headers= { 'User-agent': 'Mozilla/5.0' })
        u = urllib.request.urlopen(req)
        text = u.read()
        u.close()
        text = text.decode("utf8")
        return text
    else :
        u = urllib.request.urlopen(url)
        text = u.read()
        u.close()
        text = text.decode("utf8")
        return text