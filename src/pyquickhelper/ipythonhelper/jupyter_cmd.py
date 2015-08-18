"""
@file
@brief Jupyter command line
"""
import os
import sys

from ..loghelper import run_cmd, noLOG
from .notebook_exception import JupyterException


def get_jupyter_program(exe=None):
    """
    get jupyter executable

    @param      exe             path to python executable
    @return                     jupyter executable
    """
    if exe is None:
        exe = os.path.dirname(sys.executable)
    if sys.platform.startswith("win"):
        if not exe.endswith("Scripts"):
            ipy = os.path.join(exe, "Scripts", "jupyter.exe")
            if not os.path.exists(ipy):
                raise FileNotFoundError(ipy)
        else:
            ipy = os.path.join(exe, "jupyter.exe")
            if not os.path.exists(ipy):
                raise FileNotFoundError(ipy)
    else:
        ipy = os.path.join(exe, "jupyter")

    return ipy


def jupyter_cmd(exe=None, args=None, fLOG=noLOG):
    """
    run jupyter command line

    @param      exe     @see fn get_jupyter_program
    @param      args    list of arguments, if None, return the help
    @param      fLOG    logging function
    @return             output
    """
    jup = get_jupyter_program(exe)
    if args is None:
        args = ["-h"]
    cmd = jup + " " + " ".join(args)
    out, err = run_cmd(cmd, wait=True, fLOG=fLOG)
    if args == ["-h"]:
        out += "\n" + err
    elif:
        if len(err) > 0:
            raise JupyterException(
                "unable to run\nCMD:\n{0}\nOUT:\n{1}\nERR:\n{2}".format(cmd, out, err))
    return out
