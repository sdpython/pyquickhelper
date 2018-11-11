# -*- coding: utf-8 -*-
"""
@file
@brief Some functions about HTML
"""
import base64


def html_in_frame(htext, style="width:100%;height:100%;"):
    """
    Inserts :epkg:`HTML` text into a frame in binary format.

    @param      htext           string to clean
    @param      style           HTML style
    @return                     HTML string
    """
    html = "data:text/html;base64," + base64.b64encode(htext.encode('utf8')).decode('utf8')  # noqa
    return '<iframe src="{html}" style="{style}"></iframe>'.format(html=html, style=style)
