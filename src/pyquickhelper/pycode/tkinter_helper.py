"""
@file
@brief  Helpers for tkinter

.. versionadded:: 1.1
"""
import os
import sys


def fix_tkinter_issues_virtualenv():
    """
    fix an issue which happens in a virtual environment,
    see `Fix Tcl inside a virtualenv on Windows <https://github.com/pypa/virtualenv/pull/627>`_
    """
    def location():
        import numpy
        site = os.path.dirname(os.path.join(os.path.abspath(numpy.__file__)))
        rev = os.path.join(site, "..", "..", "..")
        if sys.platform.startswith("win"):
            site = os.path.join(rev, "tcl")
            if not os.path.exists(site):
                mes = ", ".join(os.listdir(rev))
                raise FileNotFoundError(
                    "unable to find: {0},\nsubfolders: {1}".format(site, mes))
        else:
            site = os.path.join(rev, "..", "tcl")
            if not os.path.exists(site):
                mes = ", ".join(os.listdir(os.path.join(rev, "..")))
                raise FileNotFoundError(
                    "unable to find: {0},\nsubfolders: {1}".format(site, mes))
        return os.path.normpath(site)

    def look_for(where, prefix):
        lst = sorted(os.listdir(where), reverse=True)
        l = len(prefix)
        for _ in lst:
            if _.startswith(prefix) and "0" <= _[l] <= "9" and ".lib" not in _:
                return os.path.join(where, _)
        raise FileNotFoundError("unable to find any folder starting with {0} in {1}\nLIST:\n{2}".format(
            prefix, where, ", ".join(lst)))

    if "TCL_LIBRARY" not in os.environ:
        loc = location()
        p = look_for(loc, "tcl")
        os.environ["TCL_LIBRARY"] = p

    if "TK_LIBRARY" not in os.environ:
        loc = location()
        p = look_for(loc, "tk")
        os.environ["TK_LIBRARY"] = p

    if "TIX_LIBRARY" not in os.environ:
        loc = location()
        p = look_for(loc, "tix")
        os.environ["TIX_LIBRARY"] = p

    return os.environ["TCL_LIBRARY"], os.environ["TK_LIBRARY"], os.environ["TIX_LIBRARY"]
