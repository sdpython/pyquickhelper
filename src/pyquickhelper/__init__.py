# -*- coding: utf-8 -*-
"""
@file
@brief Module *pyquickhelper*.
Helpers to produce documentation, test notebooks, walk through files,
sphinx extension, jenkins helpers...
"""

__version__ = "1.10.3616"
__author__ = "Xavier Dupré"
__github__ = "https://github.com/sdpython/pyquickhelper"
__url__ = "http://www.xavierdupre.fr/app/pyquickhelper/helpsphinx/index.html"
__license__ = "MIT License"
__blog__ = """
<?xml version="1.0" encoding="UTF-8"?>
<opml version="1.0">
    <head>
        <title>blog</title>
    </head>
    <body>
        <outline text="pyquickhelper"
            title="pyquickhelper"
            type="rss"
            xmlUrl="http://www.xavierdupre.fr/app/pyquickhelper/helpsphinx/_downloads/rss.xml"
            htmlUrl="http://www.xavierdupre.fr/app/pyquickhelper/helpsphinx/blog/main_0000.html" />
    </body>
</opml>
"""


def check():
    """
    Checks the library is working.
    It raises an exception if it does not.

    @return         boolean
    """
    from .loghelper import check_log
    check_log()
    return True


def _setup_hook(add_print=False, unit_test=False):
    """
    if this function is added to the module,
    the help automation and unit tests call it first before
    anything goes on as an initialization step.
    It should be run in a separate process.

    @param      add_print       print *Success: _setup_hook*
    @param      unit_test       used only for unit testing purpose
    """
    # it can check many things, needed module
    # any others things before unit tests are started
    if add_print:
        print("Success: _setup_hook")  # pragma: no cover


def load_ipython_extension(ip):  # pragma: no cover
    """
    to allow the call ``%load_ext pyquickhelper``

    @param      ip      from ``get_ipython()``
    """
    from .ipythonhelper.magic_class_example import register_file_magics as freg
    freg(ip)
    from .ipythonhelper.magic_class_compress import register_file_magics as creg
    creg(ip)
    from .ipythonhelper.magic_class_diff import register_file_magics as dreg
    dreg(ip)
    from .ipythonhelper.magic_class_crypt import register_file_magics as ereg
    ereg(ip)


def get_fLOG(log=True):
    """
    return a logging function

    @param      log     True, return @see fn fLOG, otherwise @see fn noLOG
    @return             function
    """
    if log:
        from .loghelper import fLOG
        return fLOG
    else:
        from .loghelper import noLOG
        return noLOG


def get_insetup_functions():
    """
    Returns function used when a module includes C++ parts.

    @return     tuple of functions
    """
    from .pycode.insetup_helper import must_build, run_build_ext
    return must_build, run_build_ext
