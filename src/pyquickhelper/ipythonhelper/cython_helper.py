"""
@file
@brief Notebook makes it easy to use Cython.
"""

import sys
import os


def ipython_cython_extension():
    """
    The function raises an exception if cython has a good chance not
    to work because Python does not find any suitable compiler
    (not :epkg:`MinGW` or :epkg:`Visual Studio Community Edition` or any expected version).
    In that case, the function displays a message with some indications
    on how to fix it.

    .. faqref::
        :title: Cython does not work on Windows?
        :index: vcvarsall, cython

        This raises the following message::

            Unable to find vcvarsall.bat

        The blogpost
        `Build a Python 64 bit extension on Windows <http://www.xavierdupre.fr/blog/2013-07-07_nojs.html>`_
        answers that question.
        One file needs to be modified::

            <python>\\lib\\distutils\\msvc9compiler.py
    """
    if not sys.platform.startswith("win"):
        return True

    import distutils.msvc9compiler as mod
    fc = os.path.abspath(mod.__file__)
    with open(fc, "r") as f:
        code = f.read()

    find = "'win-amd64' : 'x86_amd64'"
    if find not in code:
        url = "http://www.xavierdupre.fr/blog/2013-07-07_nojs.html"
        raise Exception(
            'Unable to find string {1} in\n  File "{0}", line 1\nsee {2}'.format(fc, find, url))

    return True
