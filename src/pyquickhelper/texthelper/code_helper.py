# -*- coding: utf-8 -*-
"""
@file
@brief Some functions about diacritics
"""
import re
import keyword


def change_style(name):
    """
    Switches from *AaBb* into *aa_bb*.

    @param      name    name to convert
    @return             converted name

    Example:

    ::

        changeStyle --> change__style
    """
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    return s2 if not keyword.iskeyword(s2) else s2 + "_"
