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

    .. runpython::
        :showcode:

        from pyquickhelper.texthelper import change_style

        print("changeStyle --> {0}".format(change_style('change_style')))
    """
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    return s2 if not keyword.iskeyword(s2) else s2 + "_"


def add_rst_links(text, values, tag="epkg", n=4):
    """
    Replaces words by something like ``:epkg:'word'``.

    @param      text        text to process
    @param      values      values
    @param      tag         tag to use
    @param      n           number of consecutive words to look at
    @return                 new text

    .. runpython::
        :showcode:

        from pyquickhelper.texthelper import add_rst_links
        text = "Maybe... Python is winning the competition for machine learning language."
        values = {'Python': 'https://www.python.org/',
                  'machine learning': 'https://en.wikipedia.org/wiki/Machine_learning'}
        print(add_rst_links(text, values))
    """
    def replace(words, i, n):
        mx = max(len(words), i + n)
        for last in range(mx, i, -1):
            w = ''.join(words[i:last])
            if w in values:
                return last, ":{0}:`{1}`".format(tag, w)
        return i + 1, words[i]

    reg = re.compile("(([\\\"_*`\\w']+)|([\\W]+)|([ \\n]+))")
    words = reg.findall(text)
    words = [_[0] for _ in words]
    res = []
    i = 0
    while i < len(words):
        i, w = replace(words, i, n)
        res.append(w)
    return ''.join(res)
