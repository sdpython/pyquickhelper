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

    src = SourceRepository(commandline=commandline)
    last = src.get_last_commit_hash(proj)
    cmd = ["--token={0}".format(token), "--file={0}".format(report),
           "--commit={0}".format(last), "--root={0} -X gcov".format(proj)]
    if token is not None:
        import codecov
        codecov.main(cmd)
        if err:
            raise Exception(
                "unable to run:\nCMD:\n{0}\nOUT:\n{1}\nERR:\n{2}".format(cmd, out, err))
        return out, err
    else:
        return cmd
