"""
@file
@brief Function to use inside setup.py

.. versionadded:: 1.5
"""
import os
import sys

from .. loghelper import run_cmd


def must_build(argv=None):
    """
    Determines if the module must be built before running the command
    in *argv*.

    @param      argv        if None, default to sys.argv
    @return                 boolean

    *built* means calling ``setup.py build_ext --inplace``.
    """
    if argv is None:
        argv = sys.argv
    for k in {'unittests', 'unittests_LONG', 'unittests_SKIP', 'unittests_GUI', 'build_sphinx'}:
        if k in argv:
            return True
    return False


def run_build_ext(setup_file):
    """
    Run ``setup.py build_ext --inplace``.

    @param      setup_file      setup_file
    @return                     output
    """
    exe = sys.executable
    setup = os.path.join(os.path.abspath(
        os.path.dirname(setup_file)), "setup.py")
    cmd = "{0} {1} build_ext --inplace".format(exe, setup)
    chd = os.path.abspath(os.path.dirname(setup_file))
    out, err = run_cmd(cmd, wait=True, change_path=chd)
    err0 = _filter_out_warning(err)
    if len(err0) > 0:
        mes = "Unable to run\n{0}\n[pyqerror]\n{1}".format(cmd,
                                                           "\n".join("### " + _ for _ in err.split("\n")))
        raise Exception(mes)
    return out


def _filter_out_warning(out):
    """
    Filters out (import) warning from error

    @param      out     string
    @return             filtered string
    """
    lines = out.split("\n")
    new_lines = []
    skip = False
    for line in lines:
        if len(line) == 0:
            skip = True
        elif line[0] != " ":
            skip = "ImportWarning" in line
        if not skip:
            new_lines.append(line)
    return "\n".join(new_lines)
