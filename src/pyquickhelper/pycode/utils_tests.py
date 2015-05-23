"""
@file
@brief  This extension contains various functionalities to help unittesting.

.. versionchanged:: 1.1
    Moved to folder ``pycode``.
"""
from __future__ import print_function

import os
import stat
import sys
import glob
import re
import unittest
import io
import warnings
import time

from ..filehelper.synchelper import remove_folder
from ..loghelper.flog import fLOG, run_cmd
from ..pycode.call_setup_hook import call_setup_hook


__all__ = ["get_temp_folder", "main_wrapper_tests"]


def get_temp_folder(thisfile, name, clean=True, create=True):
    """
    return a local temporary folder to store files when unit testing

    @param      thisfile        use ``__file__``
    @param      name            name of the temporary folder
    @param      clean           if True, clean the folder first
    @param      create          if True, creates it (empty if clean is True)
    @return                     temporary folder

    .. versionadded:: 0.9
    """
    if not name.startswith("temp_"):
        raise NameError("the folder {0} must begin with temp_".format(name))

    local = os.path.join(
        os.path.normpath(os.path.abspath(os.path.dirname(thisfile))), name)
    if name == local:
        raise NameError(
            "the folder {0} must be relative, not absolute".format(name))

    if not os.path.exists(local):
        if create:
            os.mkdir(local)
            mode = os.stat(local).st_mode
            nmode = mode | stat.S_IWRITE
            if nmode != mode:
                os.chmod(local, nmode)
    else:
        if clean:
            remove_folder(local)
            time.sleep(0.1)
        if create and not os.path.exists(local):
            os.mkdir(local)
            mode = os.stat(local).st_mode
            nmode = mode | stat.S_IWRITE
            if nmode != mode:
                os.chmod(local, nmode)

    return local


def get_test_file(filter, dir=None, no_subfolder=False):
    """
    return the list of test files
    @param      dir             path to look (or paths to look if it is a list)
    @param      filter          only select files matching the pattern (ex: test*)
    @param      no_subfolder    the function investigates the folder *dir* and does not try any subfolder in
                                ``{"_nrt", "_unittest", "_unittests"}``
    @return                     a list of test files

    .. versionchanged:: 1.1
        Parameter *no_subfolder* was added.
    """
    if no_subfolder:
        dirs = [dir]
    else:
        expected = {"_nrt", "_unittest", "_unittests"}
        if dir is None:
            path = os.path.split(__file__)[0]
            dirs = [os.path.join(path, "..", "..", d) for d in expected]
        elif isinstance(dir, str  # unicode#
                        ):
            if not os.path.exists(dir):
                raise FileNotFoundError(dir)
            last = os.path.split(dir)[-1]
            if last in expected:
                dirs = [dir]
            else:
                dirs = [os.path.join(dir, d) for d in expected]
        else:
            dirs = dir
            for d in dirs:
                if not os.path.exists(d):
                    raise FileNotFoundError(d)

    copypaths = list(sys.path)

    li = []
    for dir in dirs:
        if "__pycache__" in dir:
            continue
        if not os.path.exists(dir):
            continue
        if dir not in sys.path and dir != ".":
            sys.path.append(dir)
        li += glob.glob(dir + "/" + filter)
        if filter != "temp_*":
            li = [l for l in li if "test_" in l and ".py" in l and
                  "test_main" not in l and
                  "temp_" not in l and
                  "out.test_copyfile.py.2.txt" not in l and
                  ".pyc" not in l and
                  ".pyd" not in l and
                  ".so" not in l and
                  ".py~" not in l and
                  ".pyo" not in l]

        lid = glob.glob(dir + "/*")
        for l in lid:
            if os.path.isdir(l):
                temp = get_test_file(filter, l, no_subfolder=True)
                temp = [t for t in temp]
                li.extend(temp)

    # we restore sys.path
    sys.path = copypaths

    return li


def get_estimation_time(file):
    """
    return an estimation of the processing time, it extracts the number in ``(time=5s)`` for example

    @param      file        filename
    @return                 int
    """
    try:
        f = open(file, "r")
        li = f.readlines()
        f.close()
    except UnicodeDecodeError:
        try:
            f = open(file, "r", encoding="latin-1")
            li = f.readlines()
            f.close()
        except Exception as ee:
            raise Exception("issue with %s\n%s" % (file, str(ee)))

    s = ''.join(li)
    c = re.compile("[(]time=([0-9]+)s[)]").search(s)
    if c is None:
        return 0
    else:
        return int(c.groups()[0])


def import_files(li):
    """
    run all tests in file list li

    @param      li      list of files (python scripts)
    @return             list of tests [ ( testsuite, file) ]
    """
    allsuite = []
    for l in li:

        copypath = list(sys.path)

        sdir = os.path.split(l)[0]
        if sdir not in sys.path:
            sys.path.append(sdir)
        tl = os.path.split(l)[1]
        fi = tl.replace(".py", "")

        if fi in ["neural_network", "test_c",
                  "test_model", "test_look_up",
                  "test_look_up.extract.txt"]:
            try:
                mo = __import__(fi)
            except Exception as e:
                print("unable to import ", fi)
                mo = None
        else:
            try:
                mo = __import__(fi)
            except:
                print("problem with ", fi)
                mo = __import__(fi)

        # some tests can mess up with the import path
        sys.path = copypath

        cl = dir(mo)
        for c in cl:
            if len(c) < 5 or c[:4] != "Test":
                continue
            # test class c
            testsuite = unittest.TestSuite()
            loc = locals()
            exec(
                compile("di = dir (mo." + c + ")", "", "exec"), globals(), loc)
            di = loc["di"]
            for d in di:
                if len(d) >= 6 and d[:5] == "_test":
                    raise RuntimeError(
                        "a function _test is still deactivated %s in %s" % (d, c))
                if len(d) < 5 or d[:4] != "test":
                    continue
                # method d.c
                loc = locals()
                exec(
                    compile("t = mo." + c + "(\"" + d + "\")", "", "exec"), globals(), loc)
                t = loc["t"]
                testsuite.addTest(t)
            allsuite.append((testsuite, l))

    return allsuite


def clean(dir=None):
    """
    do the cleaning
    """
    # do not use SVN here just in case some files are not checked in.
    print()
    for log_file in ["temp_hal_log.txt", "temp_hal_log2.txt",
                     "temp_hal_log_.txt", "temp_log.txt", "temp_log2.txt", ]:
        li = get_test_file(log_file, dir=dir)
        for l in li:
            try:
                if os.path.isfile(l):
                    os.remove(l)
            except Exception as e:
                print(
                    "unable to remove file", l, " --- ", str(e).replace("\n", " "))

    li = get_test_file("temp_*")
    for l in li:
        try:
            if os.path.isfile(l):
                os.remove(l)
        except Exception as e:
            print("unable to remove file. ", l,
                  " --- ", str(e).replace("\n", " "))
    for l in li:
        try:
            if os.path.isdir(l):
                remove_folder(l)
        except Exception as e:
            print("unable to remove dir. ", l,
                  " --- ", str(e).replace("\n", " "))


def main(runner,
         path_test=None,
         limit_max=1e9,
         log=False,
         skip=-1,
         skip_list=None,
         on_stderr=False,
         flogp=print,
         processes=False,
         skip_function=None):
    """
    run all unit test
    the function looks into the folder _unittest and extract from all files
    beginning by `test_` all methods starting by `test_`.
    Each files should mention an execution time.
    Tests are sorted by increasing order.

    @param      runner          unittest Runner
    @param      path_test       path to look, if None, looks for defaults path related to this project
    @param      limit_max       avoid running tests longer than limit seconds
    @param      log             if True, enables intermediate files
    @param      skip            if skip != -1, skip the first "skip" test files
    @param      skip_list       skip unit test id in this list (by index, starting by 1)
    @param      skip_function   function(filename,content) --> boolean to skip a unit test
    @param      on_stderr       if True, publish everything on stderr at the end
    @param      flogp           logging, printing function
    @param      processes       to run the unit test in a separate process (with function @see fn run_cmd),
                                however, to make that happen, you need to specify
                                ``exit=False`` for each test file, see `unittest.main <https://docs.python.org/3.4/library/unittest.html#unittest.main>`_
    @return                     dictionnary: ``{ "err": err, "tests":list of couple (file, test results) }``

    .. versionchanged:: 0.9
        change the result type into a dictionary, catches warning when running unit tests,
        add parameter *processes* to run the unit test in a different process through command line

    .. versionchanged:: 1.0
        parameter *skip_function* was added
    """
    if skip_list is None:
        skip_list = set()
    else:
        skip_list = set(skip_list)

    # checking that the module does not belong to the installed modules
    if path_test is not None:
        path_module = os.path.join(sys.executable, "Lib", "site-packages")
        paths = [os.path.join(path_module, "src"), ]
        for path in paths:
            if os.path.exists(path):
                raise FileExistsError("this path should not exist " + path)

    def short_name(l):
        cut = os.path.split(l)
        cut = os.path.split(cut[0])[-1] + "/" + cut[-1]
        return cut

    # sort the test by increasing expected time
    print("path_test", path_test)
    li = get_test_file("test*", dir=path_test)
    est = [get_estimation_time(l) for l in li]
    co = [(e, short_name(l), l) for e, l in zip(est, li)]
    co.sort()
    cco = []

    # we check we do not run twice the same file
    done = {}
    duplicate = []
    for a, cut, l in cco:
        if cut in done:
            duplicate.append((cut, l))
        done[cut] = True

    if len(duplicate) > 0:
        s = list(set(duplicate))
        s.sort()
        mes = "\n".join(s)
        raise Exception("duplicated test file were detected:\n" + mes)

    # check existing
    if len(co) == 0:
        raise Exception(
            "unable to find any test files in {0}".format(path_test))

    if skip != -1:
        flogp("found ", len(co), " test files skipping", skip)
    else:
        flogp("found ", len(co), " test files")

    # extract the test classes
    index = 0
    for e, cut, l in co:
        if e > limit_max:
            continue
        if skip == -1 or index >= skip:
            flogp("% 3d - time " % (len(cco) + 1), "% 3d" % e, "s  --> ", cut)
        cco.append((e, l))
        index += 1

    exp = re.compile("Ran ([0-9]+) tests? in ([.0-9]+)s")

    # run the test
    li = [a[1] for a in cco]
    lis = [os.path.split(_)[-1] for _ in li]
    suite = import_files(li)
    keep = []

    # redirect standard output, err
    memout = sys.stdout
    fail = 0
    allwarn = []

    stderr = sys.stderr
    fullstderr = io.StringIO()

    for i, s in enumerate(suite):
        if skip >= 0 and i < skip:
            continue
        if i + 1 in skip_list:
            continue
        if skip_function is not None:
            with open(s[1], "r") as f:
                content = f.read()
            if skip_function(s[1], content):
                continue

        cut = os.path.split(s[1])
        cut = os.path.split(cut[0])[-1] + "/" + cut[-1]
        zzz = "running test % 3d, %s" % (i + 1, cut)
        zzz += (60 - len(zzz)) * " "
        memout.write(zzz)

        if log:
            fLOG(OutputPrint=True)
            fLOG(Lock=True)

        newstdr = io.StringIO()
        keepstdr = sys.stderr
        sys.stderr = newstdr
        list_warn = []

        if processes:
            cmd = sys.executable.replace("w.exe", ".exe") + " " + li[i]
            out, err = run_cmd(cmd, wait=True)
            if len(err) > 0:
                sys.stderr.write(err)
        else:
            if sys.version_info[0] >= 3:
                with warnings.catch_warnings(record=True) as w:
                    warnings.simplefilter("always")
                    r = runner.run(s[0])
                    for ww in w:
                        list_warn.append(ww)
                    warnings.resetwarnings()

                out = r.stream.getvalue()
            else:
                print("running")
                r = runner.run(s[0])
                out = r.stream.getvalue()
                print("end running")

        ti = exp.findall(out)[-1]
        # don't modify it, PyCharm does not get it right (ti is a tuple)
        add = " ran %s tests in %ss" % ti

        sys.stderr = keepstdr

        if log:
            fLOG(Lock=False)

        memout.write(add)

        if not r.wasSuccessful():
            err = out.split("===========")
            err = err[-1]
            memout.write("\n")
            memout.write(err)
            fail += 1

            fullstderr.write("\n#-----" + lis[i] + "\n")
            fullstderr.write("OUT:\n")
            fullstderr.write(out)
            fullstderr.write("ERRo:\n")
            fullstderr.write(err)
            fullstderr.write("WARN:\n")
            if len(list_warn) > 0:
                fullstderr.write("WARN:\n")
                for w in list_warn:
                    fullstderr.write("w{0}: {1}\n".format(i, str(w)))
            fullstderr.write("ERR:\n")
            fullstderr.write(newstdr.getvalue())
        else:
            allwarn.append((lis[i], list_warn))
            val = newstdr.getvalue()
            if len(val) > 0 and is_valid_error(val):
                fullstderr.write("\n*-----" + lis[i] + "\n")
                if len(list_warn) > 0:
                    fullstderr.write("WARN:\n")
                    for w in list_warn:
                        fullstderr.write("w{0}: {1}\n".format(i, str(w)))
                fullstderr.write("ERR:\n")
                fullstderr.write(val)

        memout.write("\n")

        keep.append((s[1], r))

    # end, catch standard output and err
    sys.stderr = stderr
    sys.stdout = memout
    val = fullstderr.getvalue()

    if len(val) > 0:
        flogp("-- STDERR (from unittests) on STDOUT")
        flogp(val)
        flogp("-- end STDERR on STDOUT")

        if on_stderr:
            sys.stderr.write("##### STDERR (from unittests) #####\n")
            sys.stderr.write(val)
            sys.stderr.write("##### end STDERR #####\n")

    if fail == 0:
        clean()

    for fi, lw in allwarn:
        if len(lw) > 0:
            memout.write("WARN: {0}\n".format(fi))
            for i, w in enumerate(lw):
                memout.write("  w{0}: {1}\n".format(i, str(w)))

    flogp("END of unit tests")

    return dict(err=val, tests=keep)


def is_valid_error(error):
    """
    checks if the text written on stderr is an error or not,
    a local server can push logs on this stream,

    it looks for keywords such as Exception, Error, TraceBack...

    @param      error       text
    @return                 boolean
    """
    keys = ["Exception", "Error", "TraceBack", "invalid", " line "]
    error = error.lower()
    for key in keys:
        if key.lower() in error:
            return True
    return False


def default_skip_function(name, code):
    """
    default skip function for function @see fn main_wrapper_tests.

    @param      name        name of the test file
    @param      code        code of the test file
    @return                 True if skipped, False otherwise
    """
    if "test_SKIP_" in name or "test_LONG_" in name:
        return True
    return False


def main_wrapper_tests(codefile,
                       skip_list=None,
                       processes=False,
                       add_coverage=False,
                       report_folder=None,
                       skip_function=default_skip_function,
                       setup_params=None):
    """
    calls function :func:`main <pyquickhelper.unittests.utils_tests.main>` and throw an exception if it fails

    @param      codefile        ``__file__`` or ``run_unittests.py``
    @param      skip_list       to skip a list of unit tests (by index, starting by 1)
    @param      processes       to run the unit test in a separate process (with function @see fn run_cmd),
                                however, to make that happen, you need to specify
                                ``exit=False`` for each test file, see `unittest.main <https://docs.python.org/3.4/library/unittest.html#unittest.main>`_
    @param      add_coverage    run the unit tests and measure the coverage at the same time
    @param      report_folder   folder where the coverage report will be stored, if None, it will be placed in:
                                ``os.path.join(os.path.dirname(codefile), "..", "_doc","sphinxdoc","source", "coverage")``
    @param      skip_function   function(filename,content) --> boolean to skip a unit test
    @param      setup_params    parameters sent to @see fn call_setup_hook

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

    """
    runner = unittest.TextTestRunner(verbosity=0, stream=io.StringIO())
    path = os.path.abspath(os.path.join(os.path.split(codefile)[0]))

    def run_main():
        res = main(runner, path_test=path, skip=-1, skip_list=skip_list, processes=processes,
                   skip_function=skip_function)
        return res

    if "win" not in sys.platform and "DISPLAY" not in os.environ:
        # issue detected with travis
        # _tkinter.TclError: no display name and no $DISPLAY environment variable
        #os.environ["DISPLAY"] = "localhost:0"
        pass

    # to deal with: _tkinter.TclError: no display name and no $DISPLAY
    # environment variable
    from .tkinter_helper import fix_tkinter_issues_virtualenv, _first_execution
    print("MODULES (1): matplotlib already imported",
          "matplotlib" in sys.modules, _first_execution)
    r = fix_tkinter_issues_virtualenv()
    print("MODULES (2): matplotlib imported",
          "matplotlib" in sys.modules, _first_execution, r)

    def tested_module(folder, project_var_name, setup_params):
        # module mod
        if setup_params is None:
            setup_params = {}
        out, err = call_setup_hook(
            folder, project_var_name, fLOG=fLOG, use_print=True, **setup_params)
        if len(err) > 0 and err != "no _setup_hook":
            raise Exception(
                "unable to run _setup_hook\n**OUT:\n{0}\n**ERR:\n{1}\n**FOLDER:\n{2}\n**NAME:\n{3}"
                .format(out, err, folder, project_var_name))

    # project_var_name
    folder = os.path.normpath(
        os.path.join(os.path.dirname(codefile), "..", "src"))
    content = [_ for _ in os.listdir(folder) if not _.startswith(
        "_") and os.path.isdir(os.path.join(folder, _))]
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

    # coverage
    if add_coverage:
        if report_folder is None:
            report_folder = os.path.join(
                os.path.abspath(os.path.dirname(codefile)), "..", "_doc", "sphinxdoc", "source", "coverage")

        print("call _setup_hook", src_abs, "name=", project_var_name)
        tested_module(src_abs, project_var_name, setup_params)
        print("end _setup_hook")

        print("current folder", os.getcwd())
        print("enabling coverage", srcp)
        from coverage import coverage
        cov = coverage(source=[srcp])
        cov.exclude('if __name__ == "__main__"')
        cov.start()

        res = run_main()

        cov.stop()
        cov.html_report(directory=report_folder)

    else:
        tested_module(src_abs, project_var_name)
        res = run_main()

    for r in res["tests"]:
        k = str(r[1])
        if "errors=0" not in k or "failures=0" not in k:
            print("*", r[1], r[0])

    err = res.get("err", "")
    if len(err) > 0:
        raise Exception(err)
