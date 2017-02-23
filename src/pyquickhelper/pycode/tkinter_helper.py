"""
@file
@brief  Helpers for tkinter

.. versionadded:: 1.1
"""
import os
import sys
import warnings

_first_execution = False


def fix_tkinter_issues_virtualenv(exc=True, fLOG=None):
    """
    Fix an issue which happens in a virtual environment,
    see `Fix Tcl inside a virtualenv on Windows <https://github.com/pypa/virtualenv/pull/627>`_

    @param      exc     raise an exception instead of a warning
    @param      fLOG    logging function
    @return             list of environment variables

    We try to deal with the following issue on Linux::

        _tkinter.TclError: no display name and no $DISPLAY

    On Linux, the solution is to run::

            import matplotlib as mpl
            mpl.use('Agg')

    But it does not work if matplotlib was already imported.
    It is recommended to delay its import
    whenever it is possible.

    .. versionchanged:: 1.5
        Raises an exception by default when used before matplotlib is imported.
        Parameters *exc* and *fLOG* were added.
    """
    global _first_execution

    def location():
        import numpy
        site = os.path.dirname(os.path.join(os.path.abspath(numpy.__file__)))
        rev = os.path.join(site, "..", "..", "..")
        if sys.platform.startswith("win"):
            site = os.path.join(rev, "tcl")
            if not os.path.exists(site):
                site2 = os.path.join(rev, "..", "tcl")
                if os.path.exists(site2):
                    site = site2
                else:
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
        lp = len(prefix)
        for _ in lst:
            if _.startswith(prefix) and "0" <= _[lp] <= "9" and ".lib" not in _:
                return os.path.join(where, _)
        raise FileNotFoundError("unable to find any folder starting with {0} in {1}\nLIST:\n{2}".format(
            prefix, where, ", ".join(lst)))

    if sys.platform.startswith("win"):
        if "matplotlib" in sys.modules:
            if _first_execution:
                warnings.warn(
                    "Cannot fix matplotlib display because it was already imported.")
                if exc:
                    raise Exception(
                        "Cannot fix matplotlib display because it was already imported.")

        if "TCL_LIBRARY" not in os.environ:
            loc = location()
            p = look_for(loc, "tcl")
            if fLOG:
                fLOG("Change {0}: '{1}' --> '{2}'".format("TCL_LIBRARY",
                                                          os.environ.get("TCL_LIBRARY", None), p))
            os.environ["TCL_LIBRARY"] = p

        if "TK_LIBRARY" not in os.environ:
            loc = location()
            p = look_for(loc, "tk")
            if fLOG:
                fLOG("Change {0}: '{1}' --> '{2}'".format("TK_LIBRARY",
                                                          os.environ.get("TK_LIBRARY", None), p))
            os.environ["TK_LIBRARY"] = p

        if "TIX_LIBRARY" not in os.environ:
            loc = location()
            p = look_for(loc, "tix")
            if fLOG:
                fLOG("Change {0}: '{1}' --> '{2}'".format("TIX_LIBRARY",
                                                          os.environ.get("TIX_LIBRARY", None), p))
            os.environ["TIX_LIBRARY"] = p

        if "DISPLAY" not in os.environ:
            p = ":0"
            if fLOG:
                fLOG("Change {0}: '{1}' --> '{2}'".format("DISPLAY",
                                                          os.environ.get("DISPLAY", None), p))
            os.environ["DISPLAY"] = p
    else:
        # if "DISPLAY" not in os.environ:
        #    os.environ["DISPLAY"] = ':10.0'
        if fLOG:
            fLOG("Call mpl.use('Agg')")
        if "matplotlib" in sys.modules:
            if _first_execution:
                warnings.warn(
                    "Cannot fix matplotlib display because it was already imported.")
                if exc:
                    raise Exception(
                        "Cannot fix matplotlib display because it was already imported.")
            import matplotlib as mpl
            mpl.use('Agg')
        else:
            import matplotlib as mpl
            mpl.use('Agg')

    _first_execution = False

    return os.environ.get("TCL_LIBRARY", None), os.environ.get("TK_LIBRARY", None), \
        os.environ.get("TIX_LIBRARY", None), os.environ.get("DISPLAY", None)
