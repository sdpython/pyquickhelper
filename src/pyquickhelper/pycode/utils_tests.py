"""
@file
@brief This extension contains various functionalities to help unittesting.
"""
import os
import sys
import unittest
from datetime import datetime
import warnings
import sqlite3
from .code_exceptions import CoverageException, SetupHookException
from .coverage_helper import publish_coverage_on_codecov, find_coverage_report, coverage_combine
from .utils_tests_stringio import StringIOAndFile


class TestWrappedException(Exception):
    "Raised by @see fn main_wrapper_tests"
    pass


def _modifies_coverage_report(name, bsrcp, bproj):
    conn = sqlite3.connect(name)
    sql = []
    for row in conn.execute("select * from file"):
        name = row[1]
        for b in bsrcp:
            name = name.replace(b, bproj)
        name = name.replace('\\', '/')
        s = "UPDATE file SET path='{}' WHERE id={};".format(name, row[0])
        sql.append(s)

    c = conn.cursor()
    for s in sql:
        c.execute(s)
    conn.commit()
    conn.close()


def main_wrapper_tests(logfile, skip_list=None, processes=False, add_coverage=False, report_folder=None,
                       skip_function=None, setup_params=None, only_setup_hook=False,
                       coverage_options=None, coverage_exclude_lines=None, additional_ut_path=None,
                       covtoken=None, hook_print=True, stdout=None, stderr=None, filter_warning=None,
                       dump_coverage=None, add_coverage_folder=None, coverage_root="src", fLOG=None):
    """
    Calls function :func:`main <pyquickhelper.unittests.utils_tests.main>`
    and throws an exception if it fails.

    @param      logfile                 locatio of a logfile
    @param      skip_list               to skip a list of unit tests (by index, starting by 1)
    @param      processes               to run the unit test in a separate process (with function @see fn run_cmd),
                                        however, to make that happen, you need to specify
                                        ``exit=False`` for each test file, see `unittest.main
                                        <https://docs.python.org/3/library/unittest.html#unittest.main>`_
    @param      add_coverage            (bool) run the unit tests and measure the coverage at the same time
    @param      report_folder           (str) folder where the coverage report will be stored
    @param      skip_function           *function(filename,content,duration) --> boolean* to skip a unit test
    @param      setup_params            parameters sent to @see fn call_setup_hook
    @param      only_setup_hook         calls only @see fn call_setup_hook, do not run the unit test
    @param      coverage_options        (dict) options for module coverage as a dictionary, see below, default is None
    @param      coverage_exclude_lines  (list) options for module coverage, lines to exclude from the coverage report, defaul is None
    @param      additional_ut_path      (list) additional paths to add when running the unit tests
    @param      covtoken                (str|tuple(str, str)) token used when publishing coverage report to `codecov <https://codecov.io/>`_
                                        or None to not publish
    @param      hook_print              enable print display when calling *_setup_hook*
    @param      stdout                  if not None, write output on this stream instead of *sys.stdout*
    @param      stderr                  if not None, write errors on this stream instead of *sys.stderr*
    @param      filter_warning          function which removes some warnings in the final output,
                                        if None, the function filters out some recurrent warnings
                                        in jupyter (signature: ``def filter_warning(w: warning) -> bool``),
                                        @see fn default_filter_warning
    @param      dump_coverage           dump or copy the coverage at this location
    @param      add_coverage_folder     additional coverage folder reports
    @param      coverage_root           subfolder for the coverage
    @param      fLOG                    ``function(*l, **p)``, logging function

    *covtoken* can be a string ``<token>`` or a
    tuple ``(<token>, <condition>)``. The condition is evaluated
    by the python interpreter and determines whether or not the coverage
    needs to be published.

    .. faqref::
        :title: How to build pyquickhelper with Jenkins?
        :index: Jenkins

        :epkg:`Jenkins` is a task scheduler for continuous integration.
        You can easily schedule batch command to build and run unit tests for a specific project.
        To build pyquickhelper, you need to install :epkg:`python`,
        :epkg:`pymyinstall`,
        :epkg:`miktex`, :epkg:`pandoc`,
        :epkg:`sphinx`.

        Once Jenkins is installed, the command to schedule is::

            set PATH=%PATH%;%USERPOFILE%\\AppData\\Local\\Pandoc
            build_setup_help_on_windows.bat

        This works if you installed Jenkins with your credentials.
        Otherwise, the path to ``pandoc.exe`` needs to be changed.
        And you can also read `Schedule builds with Jenkins
        <http://www.xavierdupre.fr/blog/2014-12-06_nojs.html>`_.
        :epkg:`node.js` might be required if a notebooks contain javascript.

    Parameters *add_coverage* and *report_folder* are used to compute the coverage
    using the module `coverage <http://nedbatchelder.com/code/coverage/>`_.
    The function does something about the following error:

            _tkinter.TclError: no display name and no $DISPLAY environment variable

    It is due to :epkg:`matplotlib`.
    See `Generating matplotlib graphs without a running X server
    <http://stackoverflow.com/questions/4931376/generating-matplotlib-graphs-without-a-running-x-server>`_.
    If the skip function is None, it will replace it by the function @see fn default_skip_function.
    Calls function @see fn _setup_hook if it is available in the unit tested module.
    Parameter *tested_module* was added, the function then checks the presence of
    function @see fn _setup_hook, it is the case, it runs it.

    Parameter *setup_params*: a mechanism was put in place
    to let the module to test a possibility to run some preprocessing steps
    in a separate process. They are described in @see fn _setup_hook
    which must be found in the main file ``__init__.py``.
    Parameter *only_setup_hook*:
    saves the report in XML format, binary format, replace full paths by relative path.

    Parameters *coverage_options*, *coverage_exclude_lines*, *additional_ut_path*:
    see class `Coverage <http://coverage.readthedocs.org/en/coverage-4.0b1/api_coverage.html?highlight=coverage#coverage.Coverage.__init__>`_
    and `Configuration files <http://coverage.readthedocs.org/en/coverage-4.0b1/config.html>`_
    to specify those options. If both values are left to None, this function will
    compute the code coverage for all files in this module. The function
    now exports the coverage options which were used.
    For example, to exclude files from the coverage report::

        coverage_options=dict(omit=["*exclude*.py"])

    Parameter *covtoken*: used to post the coverage report to
    `codecov <https://codecov.io/>`_.

    .. versionchanged:: 1.8
        Parameter *coverage_root* was added.
    """
    # delayed import
    from ..loghelper.os_helper import get_user

    if skip_function is None:  # pragma: no cover
        from .utils_tests_private import default_skip_function
        skip_function = default_skip_function

    if fLOG is None:  # pragma: no cover
        from ..loghelper.flog import noLOG
        fLOG = noLOG

    whole_ouput = StringIOAndFile(logfile)
    runner = unittest.TextTestRunner(verbosity=0, stream=whole_ouput)
    path = os.path.abspath(os.path.join(os.path.split(logfile)[0]))
    stdout_this = stdout if stdout else sys.stdout
    datetime_begin = datetime.now()

    def _find_source(fold):  # pragma: no cover
        fold0 = fold
        exists = os.path.exists(os.path.join(fold, ".gitignore"))
        while not exists:
            if len(fold) < 2:
                raise FileNotFoundError(
                    "Unable to guess source from '{0}'.".format(fold0))
            fold = os.path.split(fold)[0]
            exists = os.path.exists(os.path.join(fold, ".gitignore"))
        return os.path.normpath(os.path.abspath(fold))

    def run_main():
        # delayed import to speed up import of pycode
        from .utils_tests_private import main_run_test
        res = main_run_test(runner, path_test=path, skip=-1, skip_list=skip_list,
                            processes=processes, skip_function=skip_function,
                            additional_ut_path=additional_ut_path, stdout=stdout, stderr=stderr,
                            filter_warning=filter_warning, fLOG=fLOG)
        return res

    if "win" not in sys.platform and "DISPLAY" not in os.environ:
        # issue detected with travis
        # _tkinter.TclError: no display name and no $DISPLAY environment variable
        #os.environ["DISPLAY"] = "localhost:0"
        pass

    # other coverage reports
    if add_coverage_folder is not None and dump_coverage is not None:  # pragma: no cover
        sub = os.path.split(dump_coverage)[0]
        sub = os.path.split(sub)[-1]
        other_cov_folders = find_coverage_report(
            add_coverage_folder, exclude=sub)
        mes = "[main_wrapper_tests] other_cov_folders...sub='{0}'".format(sub)
        stdout_this.write(mes + "\n")
        for k, v in sorted(other_cov_folders.items()):
            mes = "[main_wrapper_tests]     k='{0}' v={1}".format(k, v)
            stdout_this.write(mes + "\n")
        if len(other_cov_folders) == 0:
            other_cov_folders = None
    else:
        other_cov_folders = None

    # to deal with: _tkinter.TclError: no display name and no $DISPLAY
    # environment variable
    from .tkinter_helper import fix_tkinter_issues_virtualenv, _first_execution
    fLOG("[main_wrapper_tests] MODULES (1): matplotlib already imported",
         "matplotlib" in sys.modules, "first execution", _first_execution)
    r = fix_tkinter_issues_virtualenv(fLOG=fLOG)
    fLOG("[main_wrapper_tests] MODULES (2): matplotlib imported",
         "matplotlib" in sys.modules, "first execution", _first_execution)
    fLOG("[main_wrapper_tests] fix_tkinter_issues_virtualenv", r)

    def tested_module(folder, project_var_name, setup_params):
        # module mod
        # delayed import
        from .call_setup_hook import call_setup_hook
        if setup_params is None:
            setup_params = {}
        out, err = call_setup_hook(
            folder, project_var_name, fLOG=fLOG, use_print=hook_print, **setup_params)
        if len(err) > 0 and err != "no _setup_hook":  # pragma: no cover
            # fix introduced because pip 8.0 displays annoying warnings
            # RuntimeWarning: Config variable 'Py_DEBUG' is unset, Python ABI tag may be incorrect
            # RuntimeWarning: Config variable 'WITH_PYMALLOC' is unset, Python
            # ABI tag may be incorrect
            lines = err.split("\n")
            keep = []
            for line in lines:
                line = line.rstrip("\r\t ")
                if line and not line.startswith(" ") and "RuntimeWarning: Config variable" not in line:
                    keep.append(line)
            if len(keep) > 0:
                raise SetupHookException(
                    "unable to run _setup_hook\n**OUT:\n{0}\n**[pyqerror]\n{1}\n**FOLDER:\n{2}\n**NAME:\n{3}\n**KEEP:\n{4}\n**"
                    .format(out, err, folder, project_var_name, "\n".join(keep)))
            out += "\nWARNINGS:\n" + err
            err = None
        return out, err

    # project_var_name
    folder = os.path.normpath(
        os.path.join(os.path.dirname(logfile), "..", "src"))
    if not os.path.exists(folder):
        folder = os.path.normpath(
            os.path.join(os.path.dirname(logfile), ".."))
    if not os.path.exists(folder):
        raise FileNotFoundError(folder)  # pragma: no cover

    def selec_name(folder, name):
        if name.startswith('_') or name.startswith('.'):
            return False
        if name in ('bin', 'dist', 'build'):
            return False  # pragma: no cover
        if '.egg' in name or 'dist_module27' in name:
            return False
        fold = os.path.join(folder, name)
        if not os.path.isdir(fold):
            return False
        init = os.path.join(fold, '__init__.py')
        if not os.path.exists(init):
            return False  # pragma: no cover
        return True

    content = [_ for _ in os.listdir(folder) if selec_name(folder, _)]
    if len(content) != 1:
        raise FileNotFoundError(  # pragma: no cover
            "Unable to guess the project name in '{0}', content=\n{1}\n---\n{2}\n---".format(
                folder, "\n".join(content), "\n".join(os.listdir(folder))))

    project_var_name = content[0]
    src_abs = os.path.normpath(os.path.abspath(
        os.path.join(os.path.dirname(logfile), "..")))

    root_src = os.path.join(src_abs, "src", project_var_name)
    if not os.path.exists(root_src):
        root_src = os.path.join(src_abs, project_var_name)
    if not os.path.exists(root_src):
        raise FileNotFoundError(  # pragma: no cover
            "Unable to find '{}'.".format(root_src))
    srcp = os.path.relpath(root_src, os.getcwd())

    if get_user() in srcp:
        raise FileNotFoundError(  # pragma: no cover
            "The location of the source should not contain "
            "'{0}': {1}".format(get_user(), srcp))

    if only_setup_hook:
        tested_module(src_abs, project_var_name, setup_params)

    else:
        # coverage
        if add_coverage:  # pragma: no cover
            stdout_this.write("[main_wrapper_tests] --- COVERAGE BEGIN ---\n")
            if report_folder is None:
                report_folder = os.path.join(
                    os.path.abspath(os.path.dirname(logfile)), "..", "_doc", "sphinxdoc", "source", "coverage")

            fLOG("[main_wrapper_tests] call _setup_hook",
                 src_abs, "name=", project_var_name)
            tested_module(src_abs, project_var_name, setup_params)
            fLOG("[main_wrapper_tests] end _setup_hook")

            fLOG("[main_wrapper_tests] current folder", os.getcwd())
            fLOG("[main_wrapper_tests] enabling coverage", srcp)
            dfile = os.path.join(report_folder, ".coverage")

            # we clean previous report or we create an empty folder
            if os.path.exists(report_folder):
                for afile in os.listdir(report_folder):
                    full = os.path.join(report_folder, afile)
                    os.remove(full)

            # we run the coverage
            if coverage_options is None:
                coverage_options = {}
            if "source" in coverage_options:
                coverage_options["source"].append(srcp)
            else:
                coverage_options["source"] = [srcp]
            if "data_file" not in coverage_options:
                coverage_options["data_file"] = dfile

            from coverage import coverage
            cov = coverage(**coverage_options)
            if coverage_exclude_lines is not None:
                for line in coverage_exclude_lines:
                    cov.exclude(line)
            else:
                cov.exclude("raise NotImplementedError")
            stdout_this.write("[main_wrapper_tests] ENABLE COVERAGE\n")
            cov.start()

            res = run_main()

            cov.stop()
            stdout_this.write(
                "[main_wrapper_tests] STOP COVERAGE + REPORT into '{0}\n'".format(report_folder))

            from coverage.misc import CoverageException as RawCoverageException
            try:
                cov.html_report(directory=report_folder)
            except RawCoverageException as e:
                raise RuntimeError("Unable to publish the coverage repot into '{}',"
                                   "\nsource='{}'\ndata='{}'".format(
                                       report_folder, coverage_options["source"],
                                       coverage_options.get("data_file", ''))) from e
            outfile = os.path.join(report_folder, "coverage_report.xml")
            cov.xml_report(outfile=outfile)
            cov.save()
            srcp_s = []

            # we clean absolute path from the produced files
            def clean_absolute_path():
                fLOG("[main_wrapper_tests] replace ",
                     srcp, ' by ', project_var_name)
                srcp_s.clear()
                srcp_s.extend([os.path.abspath(os.path.normpath(srcp)),
                               os.path.normpath(srcp)])
                bsrcp = [bytes(b, encoding="utf-8") for b in srcp_s]
                bproj = bytes(project_var_name, encoding="utf-8")
                for afile in os.listdir(report_folder):
                    full = os.path.join(report_folder, afile)
                    if '.coverage' in afile:
                        # sqlite3 format
                        _modifies_coverage_report(
                            full, srcp_s, project_var_name)
                    else:
                        with open(full, "rb") as f:
                            content = f.read()
                        for b in bsrcp:
                            content = content.replace(b, bproj)
                        with open(full, "wb") as f:
                            f.write(content)

            clean_absolute_path()

            # we print debug information for the coverage
            def write_covlog(covs):
                fLOG("[main_wrapper_tests] add debug information")
                outcov = os.path.join(report_folder, "covlog.txt")
                rows = []
                rows.append("COVERAGE OPTIONS")
                for k, v in sorted(coverage_options.items()):
                    rows.append("{0}={1}".format(k, v))
                rows.append("")
                rows.append("EXCLUDE LINES")
                for k in cov.get_exclude_list():
                    rows.append(k)
                rows.append("")
                rows.append("OPTIONS")
                for option_spec in sorted(cov.config.CONFIG_FILE_OPTIONS):
                    attr = option_spec[0]
                    if attr == "sort":
                        # we skip, it raises an exception with coverage 4.2
                        continue
                    v = getattr(cov.config, attr)
                    st = "{0}={1}".format(attr, v)
                    rows.append(st)
                rows.append("")

                if covs is not None:
                    for add in sorted(covs):
                        rows.append("MERGE='{0}'".format(add))

                content = "\n".join(rows)

                reps = []
                for _ in srcp_s[:1]:
                    __ = os.path.normpath(os.path.join(_, "..", "..", ".."))
                    __ += "/"
                    reps.append(__)
                    reps.append(__.replace("/", "\\"))
                    reps.append(__.replace("/", "\\\\"))
                    reps.append(__.replace("\\", "\\\\"))

                for s in reps:
                    content = content.replace(s, "")

                with open(outcov, "w", encoding="utf8") as f:
                    f.write(content)

            write_covlog(None)

            if dump_coverage is not None:
                # delayed import
                from ..filehelper import synchronize_folder
                src = os.path.dirname(outfile)
                stdout_this.write("[main_wrapper_tests] dump coverage from '{1}' to '{0}'\n".format(
                    dump_coverage, outfile))
                synchronize_folder(src, dump_coverage,
                                   copy_1to2=True, fLOG=fLOG)

                if other_cov_folders is not None:
                    source = _find_source(src)
                    if not source:
                        raise FileNotFoundError(
                            "Unable to find source '{0}' from '{1}'".format(source, src))
                    if coverage_root:
                        source_src = os.path.join(source, coverage_root)
                        if os.path.exists(source_src):
                            source = source_src
                    stdout_this.write(
                        "[main_wrapper_tests] ADD COVERAGE for source='{0}'\n".format(source))
                    covs = list(_[0] for _ in other_cov_folders.values())
                    covs.append(os.path.abspath(
                        os.path.normpath(os.path.join(src, '.coverage'))))
                    stdout_this.write(
                        "[main_wrapper_tests] ADD COVERAGE COMBINE={0}\n".format(covs))
                    stdout_this.write(
                        "[main_wrapper_tests] DUMP INTO='{0}'\n".format(src))
                    try:
                        coverage_combine(covs, src, source)
                        write_covlog(covs)
                    except Exception as e:
                        warnings.warn("[main_wrapper_tests] {}".format(
                            str(e).replace("\n", " ")))

            if covtoken:
                if isinstance(covtoken, tuple):
                    if eval(covtoken[1]):
                        # publishing token
                        mes = "[main_wrapper_tests] PUBLISH COVERAGE to codecov '{0}' EVAL ({1})".format(
                            covtoken[0], covtoken[1])
                        if stdout is not None:
                            stdout.write(mes)
                        stdout_this.write(mes + '\n')
                        fLOG(mes)
                        publish_coverage_on_codecov(
                            token=covtoken[0], path=outfile, fLOG=fLOG)
                    else:
                        fLOG(
                            "[main_wrapper_tests] skip publishing coverage to codecov due to False:", covtoken[1])
                else:
                    # publishing token
                    fLOG(
                        "[main_wrapper_tests] publishing coverage to codecov", covtoken)
                    publish_coverage_on_codecov(
                        token=covtoken, path=outfile, fLOG=fLOG)
            stdout_this.write("[main_wrapper_tests] --- COVERAGE END ---\n")
        else:
            stdout_this.write(
                "[main_wrapper_tests] --- NO COVERAGE BEGIN ---\n")
            if covtoken and (not isinstance(covtoken, tuple) or eval(covtoken[1])):
                raise CoverageException(  # pragma: no cover
                    "covtoken is not null but add_coverage is not True, coverage cannot be published")
            tested_module(src_abs, project_var_name, setup_params)
            res = run_main()
            stdout_this.write("[main_wrapper_tests] --- NO COVERAGE END ---\n")

        fLOG("[main_wrapper_tests] SUMMARY -------------------------")
        for r in res["tests"]:
            k = str(r[1])
            if "errors=0" not in k or "failures=0" not in k:
                fLOG("*", r[1], r[0])  # pragma: no cover

        fLOG("[main_wrapper_tests] CHECK EXCEPTION -----------------")
        err = res.get("err", "")
        if len(err) > 0:  # pragma: no cover
            # Remove most of the Sphinx warnings (sphinx < 1.8)
            lines = err.split("\n")
            lines = [
                _ for _ in lines if _ and "is already registered, it will be overridden" not in _]
            err = "\n".join(lines)
        if len(err) > 0:
            raise TestWrappedException(err)  # pragma: no cover

        datetime_end = datetime.now()

        rows = ["[main_wrapper_tests] END",
                "[main_wrapper_tests] begin time {0}".format(datetime_begin),
                "[main_wrapper_tests] end time {0}".format(datetime_end),
                "[main_wrapper_tests] duration {0}".format(datetime_end - datetime_begin)]
        for row in rows:
            fLOG(row)
            stdout_this.write(row + "\n")
