"""
@file
@brief This extension contains various functionalities to help unittesting.

.. versionchanged:: 1.1
    Moved to folder ``pycode``.

.. versionchanged:: 1.4
    Split into 3 files.
"""
from __future__ import print_function

import os
import sys
import unittest

from ..loghelper.flog import noLOG
from .call_setup_hook import call_setup_hook
from .code_exceptions import CoverageException, SetupHookException
from .coverage_helper import publish_coverage_on_codecov
from .utils_tests_private import default_skip_function, main_run_test


if sys.version_info[0] == 2:
    from StringIO import StringIO
    FileNotFoundError = Exception
else:
    from io import StringIO


def main_wrapper_tests(codefile, skip_list=None, processes=False, add_coverage=False, report_folder=None,
                       skip_function=default_skip_function, setup_params=None, only_setup_hook=False,
                       coverage_options=None, coverage_exclude_lines=None, additional_ut_path=None,
                       covtoken=None, hook_print=True, stdout=None, stderr=None, fLOG=noLOG):
    """
    calls function :func:`main <pyquickhelper.unittests.utils_tests.main>` and throw an exception if it fails

    @param      codefile                ``__file__`` or ``run_unittests.py``
    @param      skip_list               to skip a list of unit tests (by index, starting by 1)
    @param      processes               to run the unit test in a separate process (with function @see fn run_cmd),
                                        however, to make that happen, you need to specify
                                        ``exit=False`` for each test file, see `unittest.main <https://docs.python.org/3.4/library/unittest.html#unittest.main>`_
    @param      add_coverage            run the unit tests and measure the coverage at the same time
    @param      report_folder           folder where the coverage report will be stored, if None, it will be placed in:
                                        ``os.path.join(os.path.dirname(codefile), "..", "_doc","sphinxdoc","source", "coverage")``
    @param      skip_function           function(filename,content) --> boolean to skip a unit test
    @param      setup_params            parameters sent to @see fn call_setup_hook
    @param      only_setup_hook         calls only @see fn call_setup_hook, do not run the unit test
    @param      coverage_options        (dictionary) options for module coverage as a dictionary, see below, default is None
    @param      coverage_exclude_lines  (list) options for module coverage, lines to exclude from the coverage report, defaul is None
    @param      additional_ut_path      (list) additional paths to add when running the unit tests
    @param      covtoken                (str) token used when publishing coverage report to `codecov <https://codecov.io/>`_
                                        or None to not publish
    @param      hook_print              enable print display when calling *_setup_hook*
    @param      stdout                  if not None, write output on this stream instead of *sys.stdout*
    @param      stderr                  if not None, write errors on this stream instead of *sys.stderr*
    @param      fLOG                    function(*l, **p), logging function

    *covtoken* can be a string ``<token>`` or a
    tuple ``(<token>, <condition>)``. The condition is evaluated
    by the python interpreter and determines whether or not the coverage
    needs to be published.

    @FAQ(How to build pyquickhelper with Jenkins?)
    `Jenkins <http://jenkins-ci.org/>`_ is a task scheduler for continuous integration.
    You can easily schedule batch command to build and run unit tests for a specific project.
    To build pyquickhelper, you need to install `python <https://www.python.org/>`_,
    `pymyinstall <http://www.xavierdupre.fr/app/pymyinstall/helpsphinx/>`_,
    `miktex <http://miktex.org/>`_,
    `pandoc <http://johnmacfarlane.net/pandoc/>`_,
    `sphinx <http://sphinx-doc.org/>`_.

    Once Jenkins is installed, the command to schedule is::

        set PATH=%PATH%;%USERPOFILE%\AppData\Local\Pandoc
        build_setup_help_on_windows.bat

    This works if you installed Jenkins with your credentials.
    Otherwise the path to ``pandoc.exe`` needs to be changed.

    And you can also read `Schedule builds with Jenkins <http://www.xavierdupre.fr/blog/2014-12-06_nojs.html>`_.
    @endFAQ

    .. versionchanged:: 0.9
        Parameters *add_coverage* and *report_folder* were added to compute the coverage
        using the module `coverage <http://nedbatchelder.com/code/coverage/>`_.

    .. versionchanged:: 1.0
        Does something to avoid getting the following error::

            _tkinter.TclError: no display name and no $DISPLAY environment variable

        It is due to matplotlib. See `Generating matplotlib graphs without a running X server <http://stackoverflow.com/questions/4931376/generating-matplotlib-graphs-without-a-running-x-server>`_.

    .. versionchanged:: 1.1
        If the skip function is None, it will replace it by the function @see fn default_skip_function.
        Calls function @see fn _setup_hook if it is available in the unit tested module.
        Parameter *tested_module* was added, the function then checks the presence of
        function @see fn _setup_hook, it is the case, it runs it.

        Parameter *setup_params* was added. A mechanism was put in place
        to let the module to test a possibility to run some preprocessing steps
        in a separate process. They are described in @see fn _setup_hook
        which must be found in the main file ``__init__.py``.

    .. versionchanged:: 1.2
        Parameter *only_setup_hook* was added.
        Save the report in XML format, binary format, replace full paths by relative path.

    .. versionchanged:: 1.3
        Parameters *coverage_options*, *coverage_exclude_lines*,
        *additional_ut_path* were added.
        See class `Coverage <http://coverage.readthedocs.org/en/coverage-4.0b1/api_coverage.html?highlight=coverage#coverage.Coverage.__init__>`_
        and `Configuration files <http://coverage.readthedocs.org/en/coverage-4.0b1/config.html>`_
        to specify those options. If both values are left to None, this function will
        compute the code coverage for all files in this module. The function
        now exports the coverage options which were used.
        For example, to exclude files from the coverage report::

            coverage_options=dict(omit=["*exclude*.py"])

        Parameter *covtoken* as added to post the coverage report to
        `codecov <https://codecov.io/>`_.

        Parameters *hook_print*, *stdout*, *stderr* were added.
    """
    runner = unittest.TextTestRunner(verbosity=0, stream=StringIO())
    path = os.path.abspath(os.path.join(os.path.split(codefile)[0]))

    def run_main():
        res = main_run_test(runner, path_test=path, skip=-1, skip_list=skip_list,
                            processes=processes, skip_function=skip_function,
                            additional_ut_path=additional_ut_path, stdout=stdout, stderr=stderr,
                            fLOG=fLOG)
        return res

    if "win" not in sys.platform and "DISPLAY" not in os.environ:
        # issue detected with travis
        # _tkinter.TclError: no display name and no $DISPLAY environment variable
        #os.environ["DISPLAY"] = "localhost:0"
        pass

    # to deal with: _tkinter.TclError: no display name and no $DISPLAY
    # environment variable
    from .tkinter_helper import fix_tkinter_issues_virtualenv, _first_execution
    fLOG("MODULES (1): matplotlib already imported",
         "matplotlib" in sys.modules, _first_execution)
    r = fix_tkinter_issues_virtualenv()
    fLOG("MODULES (2): matplotlib imported",
         "matplotlib" in sys.modules, _first_execution, r)

    def tested_module(folder, project_var_name, setup_params):
        # module mod
        if setup_params is None:
            setup_params = {}
        out, err = call_setup_hook(
            folder, project_var_name, fLOG=fLOG, use_print=hook_print, **setup_params)
        if len(err) > 0 and err != "no _setup_hook":
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
                    "unable to run _setup_hook\n**OUT:\n{0}\n**ERR:\n{1}\n**FOLDER:\n{2}\n**NAME:\n{3}\n**KEEP:\n{4}\n**"
                    .format(out, err, folder, project_var_name, "\n".join(keep)))
            else:
                out += "\nWARNINGS:\n" + err
                err = None
        return out, err

    # project_var_name
    folder = os.path.normpath(
        os.path.join(os.path.dirname(codefile), "..", "src"))
    content = [_ for _ in os.listdir(folder) if not _.startswith(
        "_") and not _.startswith(".") and os.path.isdir(os.path.join(folder, _))]
    if len(content) != 1:
        raise FileNotFoundError(
            "unable to guess the project name in {0}\n{1}".format(folder, "\n".join(content)))

    project_var_name = content[0]
    src_abs = os.path.normpath(os.path.abspath(
        os.path.join(os.path.dirname(codefile), "..")))

    srcp = os.path.relpath(
        os.path.join(src_abs, "src", project_var_name), os.getcwd())

    if "USERNAME" in os.environ and os.environ["USERNAME"] in srcp:
        raise Exception(
            "The location of the source should not contain USERNAME: " + srcp)

    if only_setup_hook:
        tested_module(src_abs, project_var_name, setup_params)

    else:
        # coverage
        if add_coverage:
            if report_folder is None:
                report_folder = os.path.join(
                    os.path.abspath(os.path.dirname(codefile)), "..", "_doc", "sphinxdoc", "source", "coverage")

            fLOG("call _setup_hook", src_abs, "name=", project_var_name)
            tested_module(src_abs, project_var_name, setup_params)
            fLOG("end _setup_hook")

            fLOG("current folder", os.getcwd())
            fLOG("enabling coverage", srcp)
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
            cov.start()

            res = run_main()

            cov.stop()

            cov.html_report(directory=report_folder)
            outfile = os.path.join(report_folder, "coverage_report.xml")
            cov.xml_report(outfile=outfile)
            cov.save()

            # we clean absolute path from the produced files
            fLOG("replace ", srcp, ' by ', project_var_name)
            srcp_s = [os.path.abspath(os.path.normpath(srcp)),
                      os.path.normpath(srcp)]
            bsrcp = [bytes(b, encoding="utf-8") for b in srcp_s]
            bproj = bytes(project_var_name, encoding="utf-8")
            for afile in os.listdir(report_folder):
                full = os.path.join(report_folder, afile)
                with open(full, "rb") as f:
                    content = f.read()
                for b in bsrcp:
                    content = content.replace(b, bproj)
                with open(full, "wb") as f:
                    f.write(content)

            # we print debug information for the coverage
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
                attr, where = option_spec[:2]
                v = getattr(cov.config, attr)
                st = "{0}={2}".format(attr, where, v)
                rows.append(st)
            rows.append("")
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

            if covtoken:
                if isinstance(covtoken, tuple):
                    if eval(covtoken[1]):
                        # publishing token
                        fLOG("publishing coverage to codecov",
                             covtoken[0], "EVAL", covtoken[1])
                        publish_coverage_on_codecov(
                            token=covtoken[0], path=outfile, fLOG=fLOG)
                    else:
                        fLOG(
                            "skip publishing coverage to codecov due to False:", covtoken[1])
                else:
                    # publishing token
                    fLOG("publishing coverage to codecov", covtoken)
                    publish_coverage_on_codecov(
                        token=covtoken, path=outfile, fLOG=fLOG)
        else:
            if covtoken and (not isinstance(covtoken, tuple) or eval(covtoken[1])):
                raise CoverageException(
                    "covtoken is not null but add_coverage is not True, coverage cannot be published")
            tested_module(src_abs, project_var_name, setup_params)
            res = run_main()

        for r in res["tests"]:
            k = str(r[1])
            if "errors=0" not in k or "failures=0" not in k:
                fLOG("*", r[1], r[0])

        err = res.get("err", "")
        if len(err) > 0:
            raise Exception(err)
