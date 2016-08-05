"""
@file
@brief Publishing coverage

.. versionadded:: 1.3
"""
import os
import sys
from ..loghelper import SourceRepository, noLOG, run_cmd


if sys.version_info[0] == 2:
    FileNotFoundError = Exception


def get_codecov_program(exe=None):
    """
    get codecov executable

    @param      exe             path to python executable
    @return                     codecov executable
    """
    tried = []
    if exe is None:
        exe = os.path.dirname(sys.executable)
    if sys.platform.startswith("win"):
        if not exe.endswith("Scripts"):
            pi = os.path.join(exe, "Scripts", "codecov.exe")
            tried.append(pi)
            if not os.path.exists(pi):
                # Anaconda is different
                pi = os.path.join(exe, "Scripts", "codecov.exe")
                tried.append(pi)
                if not os.path.exists(pi):
                    raise FileNotFoundError(
                        "tried (1):\n" + "\n".join(tried))
        else:
            pi = os.path.join(exe, "codecov.exe")
            tried.append(pi)
            if not os.path.exists(pi):
                # Anaconda is different
                pi = os.path.join(exe, "codecov.exe")
                tried.append(pi)
                if not os.path.exists(pi):
                    raise FileNotFoundError(
                        "tried (2):\n" + "\n".join(tried))
    else:
        if exe is None:
            return "codecov"
        else:
            pi = os.path.join(exe, "codecov")

    return pi


def publish_coverage_on_codecov(path, token, commandline=True, fLOG=noLOG):
    """
    Publish the coverage report on `codecov <https://codecov.io/>`_.
    See blog post :ref:`blogpost_coverage_codecov`.

    @param      path            path to source
    @param      token           token on codecov
    @param      commandline     see @see cl SourceRepository
    @return                     out, err from function @see fn run_cmd
    """
    if os.path.isfile(path):
        report = path
    else:
        report = os.path.join(path, "_doc", "sphinxdoc",
                              "source", "coverage", "coverage_report.xml")

    report = os.path.normpath(report)
    if not os.path.exists(report):
        raise FileNotFoundError(report)

    proj = os.path.normpath(os.path.join(
        os.path.dirname(report), "..", "..", "..", ".."))

    exe = get_codecov_program()
    src = SourceRepository(commandline=commandline)
    last = src.get_last_commit_hash(proj)
    cmd = exe + " --token={0} --file={1} --commit={2} --root={3} -X gcov".format(
        token, report, last, proj)
    if token is not None:
        out, err = run_cmd(cmd, wait=True)
        if err:
            raise Exception(
                "unable to run:\nCMD:\n{0}\nOUT:\n{1}\nERR:\n{2}".format(cmd, out, err))
        return out, err
    else:
        return cmd
