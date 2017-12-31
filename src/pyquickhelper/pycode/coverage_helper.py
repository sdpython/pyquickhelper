"""
@file
@brief Publishing coverage

.. versionadded:: 1.3
"""
import os
import re
import sys
from collections import Counter
from contextlib import redirect_stderr, redirect_stdout
from ..loghelper import SourceRepository, noLOG


if sys.version_info[0] == 2:
    FileNotFoundError = Exception
    from StringIO import StringIO
else:
    from io import StringIO


def publish_coverage_on_codecov(path, token, commandline=True, fLOG=noLOG):
    """
    Publishes the coverage report on `codecov <https://codecov.io/>`_.
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
        new_out = StringIO()
        new_err = StringIO()
        with redirect_stdout(new_out):
            with redirect_stderr(new_err):
                codecov.main(*cmd)
        out = new_out.getvalue()
        err = new_err.getvalue()
        if err:
            raise Exception(
                "unable to run:\nCMD:\n{0}\nOUT:\n{1}\n[pyqerror]\n{2}".format(cmd, out, err))
        return out, err
    else:
        return cmd


def coverage_combine(data_files, output_path, source, process=None):
    """
    Merges multiples reports.

    @param      data_files  report files (``.coverage``)
    @param      output_path output path
    @param      source      source directory
    @param      process     function which processes the coverage report

    The function *process* should have the signature:

    ::

        def process(content):
            # ...
            return content
    """
    reg = re.compile(',\\"(.*?[.]py)\\"')

    def copy_replace(source, dest, root_source):
        with open(source, "r") as f:
            content = f.read()
        cf = reg.findall(content)
        co = Counter([_.split('src')[0] for _ in cf])
        mx = max((v, k) for k, v in co.items())
        root = mx[1].rstrip('\\/')
        if '\\\\' in root:
            s2 = root_source.replace('\\', '\\\\').replace('/', '\\\\')
        else:
            s2 = root_source
        content = content.replace(root, s2)
        with open(dest, "w") as f:
            f.write(content)

    from coverage import Coverage
    dests = [os.path.join(output_path, '.coverage{0}'.format(
        i)) for i in range(len(data_files))]
    for fi, de in zip(data_files, dests):
        copy_replace(fi, de, source)
    cov = Coverage(source=source)
    cov.combine(dests)
    cov.html_report(directory=output_path)
