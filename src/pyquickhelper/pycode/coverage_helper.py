"""
@file
@brief Publishing coverage

.. versionadded:: 1.3
"""
import os
import sys
from ..loghelper import SourceRepository, noLOG


if sys.version_info[0] == 2:
    FileNotFoundError = Exception
    from StringIO import StringIO
else:
    from io import StringIO


def publish_coverage_on_codecov(path, token, commandline=True, fLOG=noLOG):
    """
    Publish the coverage report on `codecov <https://codecov.io/>`_.
    See blog post :ref:`blogpost_coverage_codecov`.

    @param      path            path to source
    @param      token           token on codecov
    @param      commandline     see @see cl SourceRepository
    @param      fLOG            logging function
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
        out = sys.stdout
        err = sys.stderr
        new_out = StringIO()
        new_err = StringIO()
        sys.stdout = new_out
        sys.stderr = new_err
        codecov.main(*cmd)
        sys.stdout = out
        sys.stderr = err
        out = new_out.getvalue()
        err = new_err.getvalue()
        if err:
            raise Exception(
                "unable to run:\nCMD:\n{0}\nOUT:\n{1}\n[pyqerror]\n{2}".format(cmd, out, err))
        return out, err
    else:
        return cmd
