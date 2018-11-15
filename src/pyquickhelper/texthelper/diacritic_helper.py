# -*- coding: utf-8 -*-
"""
@file
@brief Some functions about diacritics
"""

import unicodedata


def remove_diacritics(input_str):
    """
    Removes diacritics.

    @param      input_str       string to clean
    @return                     cleaned string

    Example::

        enguérand --> enguerand
    """
    nkfd_form = unicodedata.normalize('NFKD', input_str)
    only_ascii = nkfd_form.encode('ASCII', 'ignore')
    return only_ascii.decode("utf8")
