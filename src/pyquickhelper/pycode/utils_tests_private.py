"""
@file
@brief This extension contains various functionalities to help unittesting.

.. versionadded:: 1.4
    Split from from utils_tests.py.
"""
from __future__ import print_function

import os
import sys
import glob
import re
import unittest
import warnings

from ..filehelper.synchelper import remove_folder
from ..loghelper.flog import run_cmd, noLOG

if sys.version_info[0] == 2:
    from StringIO import StringIO
    FileNotFoundError = Exception
    from codecs import open
else:
    from io import StringIO


def get_test_file(filter, dir=None, no_subfolder=False, fLOG=noLOG, root=None):
    """
    return the list of test files
    @param      dir             path to look (or paths to look if it is a list)
    @param      filter          only select files matching the pattern (ex: test*)
    @param      no_subfolder    the function investigates the folder *dir* and does not try any subfolder in
                                ``{"_nrt", "_unittest", "_unittests"}``
    @param      fLOG            logging function
    @param      root            root or folder which contains the project,
                                rules applyong on folder name will not apply on it
    @return                     a list of test files

    .. versionchanged:: 1.1
        Parameter *no_subfolder* was added.

    .. versionchanged:: 1.3
        Paramerer *fLOG*, *root* were added.
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
    fLOG("[unittests], inspecting", dirs)

    li = []
    for dir in dirs:
        if "__pycache__" in dir or "site-packages" in dir:
            continue
        if not os.path.exists(dir):
            continue
        if dir not in sys.path and dir != ".":
            sys.path.append(dir)
        content = glob.glob(dir + "/" + filter)
        if filter != "temp_*":
            if root is not None:
                def remove_root(p):
                    if p.startswith(root):
                        return p[len(root):]
                    else:
                        return p
                content = [(remove_root(l), l) for l in content]
            else:
                content = [(l, l) for l in content]

            content = [fu for l, fu in content if "test_" in l and
                       ".py" in l and
                       "test_main" not in l and
                       "temp_" not in l and
                       "out.test_copyfile.py.2.txt" not in l and
                       ".pyc" not in l and
                       ".pyd" not in l and
                       ".so" not in l and
                       ".py~" not in l and
                       ".pyo" not in l]
        li.extend(content)

        lid = glob.glob(dir + "/*")
        for l in lid:
            if os.path.isdir(l):
                temp = get_test_file(
                    filter, l, no_subfolder=True, fLOG=fLOG, root=root)
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
        f = open(file, "r", errors="ignore")
        li = f.readlines()
        f.close()
    except Exception as e:
        warnings.warn("issue with '{0}'\n{1}\n{2}".format(file, type(e), e))
        return 10
    try:
        s = ''.join(li)
    except Exception as e:
        warnings.warn("Probably an enconding issue for file '{0}'\n{1}\n{2}".format(file, type(e), e))
        return 10
    c = re.compile("[(]time=([0-9]+)s[)]").search(s)
    if c is None:
        return 0
    else:
        return int(c.groups()[0])


def import_files(li, additional_ut_path=None, fLOG=noLOG):
    """
    run all tests in file list li

    @param      li                      list of files (python scripts)
    @param      additional_ut_path      additional paths to add when running the unit tests
    @param      fLOG                    logging function
    @return                             list of tests [ ( testsuite, file) ]

    .. versionchanged:: 1.3
        Parameters *fLOG*, *additional_ut_path* were added.
    """
    allsuite = []
    for l in li:

        copypath = list(sys.path)

        sdir = os.path.split(l)[0]
        if sdir not in sys.path:
            sys.path.append(sdir)
        if additional_ut_path:
            for p in additional_ut_path:
                if isinstance(p, tuple):
                    if p[1]:
                        sys.path.insert(0, p[0])
                    else:
                        sys.path.append(p[0])
                else:
                    sys.path.append(p)
        tl = os.path.split(l)[1]
        fi = tl.replace(".py", "")

        try:
            mo = __import__(fi)
        except:
            fLOG("problem with ", fi)
            fLOG("additional paths")
            for p in sys.path:
                fLOG("   ", p)
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


def clean(dir=None, fLOG=noLOG):
    """
    do the cleaning

    @param      dir     directory
    @param      fLOG    logging function
    """
    # do not use SVN here just in case some files are not checked in.
    for log_file in ["temp_hal_log.txt", "temp_hal_log2.txt",
                     "temp_hal_log_.txt", "temp_log.txt", "temp_log2.txt", ]:
        li = get_test_file(log_file, dir=dir)
        for l in li:
            try:
                if os.path.isfile(l):
                    os.remove(l)
            except Exception as e:
                fLOG(
                    "unable to remove file", l, " --- ", str(e).replace("\n", " "))

    li = get_test_file("temp_*")
    for l in li:
        try:
            if os.path.isfile(l):
                os.remove(l)
        except Exception as e:
            fLOG("unable to remove file. ", l,
                 " --- ", str(e).replace("\n", " "))
    for l in li:
        try:
            if os.path.isdir(l):
                remove_folder(l)
        except Exception as e:
            fLOG("unable to remove dir. ", l,
                 " --- ", str(e).replace("\n", " "))


def default_filter_warning(w):
    """
    filters out warning

    @param      w       warning
    @return             boolean (True to keep it)

    Interesting fields: ``w.message``, ``w.category``, ``w.filename``, ``w.lineno``.

    .. todoext::
        :title: filter warnings after the unit tests
        :tag: done
        :date: 2016-07-05
        :hidden:
        :issue: 19
        :release: 1.4
        :cost: 0.2

        Parameter *filter_warning* was added to give users
        a way to define their own filtering.
    """
    if isinstance(w.message, DeprecationWarning):
        if w.filename.endswith("kernelspec.py"):
            return False
        if "jupyter_client" in w.filename:
            return False
        if "IPython" in w.filename:
            if "DisplayFormatter." in str(w.message):
                return False
            if "ScriptMagics." in str(w.message):
                return False
            if "HistoryManager." in str(w.message):
                return False
            if "ProfileDir." in str(w.message):
                return False
            if "InteractiveShell." in str(w.message):
                return False
            if "on_trait_change" in str(w.message):
                return False
            if "PlainTextFormatter." in str(w.message):
                return False
            if "Metadata should be set using the .tag()" in str(w.message):
                return False
        elif "nbconvert" in w.filename:
            if "SlidesExporter." in str(w.message):
                return False
            if "TemplateExporter." in str(w.message):
                return False
            if "HTMLExporter." in str(w.message):
                return False
            if "SVG2PDFPreprocessor." in str(w.message):
                return False
            if "on_trait_change" in str(w.message):
                return False
            if "PresentExporter." in str(w.message):
                return False
            if "NbConvertApp." in str(w.message):
                return False
            if "RSTExporter." in str(w.message):
                return False
            if "PythonExporter." in str(w.message):
                return False
            if "LatexExporter." in str(w.message):
                return False
            if "Metadata should be set using the .tag()" in str(w.message):
                return False
        elif "jupyter_core" in w.filename:
            if "JupyterApp." in str(w.message):
                return False
        elif "docutils" in w.filename:
            if "'U' mode is deprecated" in str(w.message):
                return False
        elif "sympy" in w.filename:
            if "inspect.getargspec() is deprecated" in str(w.message):
                return False
    elif isinstance(w.message, ImportWarning):
        if w.filename.endswith("_bootstrap_external.py"):
            return False
    return True


def main_run_test(runner, path_test=None, limit_max=1e9, log=False, skip=-1, skip_list=None,
                  on_stderr=False, flogp=noLOG, processes=False, skip_function=None,
                  additional_ut_path=None, stdout=None, stderr=None, filter_warning=None,
                  fLOG=noLOG):
    """
    run all unit test
    the function looks into the folder _unittest and extract from all files
    beginning by `test_` all methods starting by `test_`.
    Each files should mention an execution time.
    Tests are sorted by increasing order.

    @param      runner              unittest Runner
    @param      path_test           path to look, if None, looks for defaults path related to this project
    @param      limit_max           avoid running tests longer than limit seconds
    @param      log                 if True, enables intermediate files
    @param      skip                if skip != -1, skip the first "skip" test files
    @param      skip_list           skip unit test id in this list (by index, starting by 1)
    @param      skip_function       *function(filename,content,duration) --> boolean* to skip a unit test
    @param      on_stderr           if True, publish everything on stderr at the end
    @param      flogp               logging, printing function
    @param      processes           to run the unit test in a separate process (with function @see fn run_cmd),
                                    however, to make that happen, you need to specify
                                    ``exit=False`` for each test file, see `unittest.main <https://docs.python.org/3.4/library/unittest.html#unittest.main>`_
    @param      additional_ut_path  additional paths to add when running the unit tests
    @param      stdout              if not None, use this stream instead of *sys.stdout*
    @param      stderr              if not None, use this stream instead of *sys.stderr*
    @param      filter_warning      function which removes some warnings in the final output,
                                    if None, the function filters out some recurrent warnings
                                    in jupyter (signature: ``def filter_warning(w: warning) -> bool``),
                                    @see fn default_filter_warning
    @param      fLOG                logging function
    @return                         dictionnary: ``{ "err": err, "tests":list of couple (file, test results) }``

    .. versionchanged:: 0.9
        change the result type into a dictionary, catches warning when running unit tests,
        add parameter *processes* to run the unit test in a different process through command line

    .. versionchanged:: 1.0
        parameter *skip_function* was added

    .. versionchanged:: 1.3
        Parameters *fLOG*, *stdout*, *stderr* were added.

    .. versionchanged:: 1.4
        Parameter *filter_warning* was added.
    """
    if skip_list is None:
        skip_list = set()
    else:
        skip_list = set(skip_list)
    if filter_warning is None:
        filter_warning = default_filter_warning

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
    fLOG("path_test", path_test)
    li = get_test_file("test*", dir=path_test, fLOG=fLOG, root=path_test)
    if len(li) == 0:
        raise FileNotFoundError("no test files in " + path_test)
    est = [get_estimation_time(l) for l in li]
    co = [(e, short_name(l), l) for e, l in zip(est, li)]
    co.sort()

    # we check we do not run twice the same file
    done = {}
    duplicate = []
    for a, cut, l in co:
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
        raise FileNotFoundError(
            "unable to find any test files in {0}".format(path_test))

    if skip != -1:
        flogp("found ", len(co), " test files skipping", skip)
    else:
        flogp("found ", len(co), " test files")

    # extract the test classes
    cco = []
    duration = {}
    index = 0
    for e, cut, l in co:
        if e > limit_max:
            continue
        cco.append((e, l))
        cut = os.path.split(l)
        cut = os.path.split(cut[0])[-1] + "/" + cut[-1]
        duration[cut] = e
        index += 1

    exp = re.compile("Ran ([0-9]+) tests? in ([.0-9]+)s")

    # run the test
    li = [a[1] for a in cco]
    lis = [os.path.split(_)[-1] for _ in li]
    suite = import_files(li, additional_ut_path=additional_ut_path, fLOG=fLOG)
    keep = []

    # redirect standard output, error
    memo_stdout = sys.stdout
    memout = sys.stdout if stdout is None else stdout
    fail = 0
    allwarn = []

    memo_stderr = sys.stderr
    memerr = sys.stderr if stderr is None else stderr
    fullstderr = StringIO()

    # displays
    memout.write("---- BEGIN UNIT TEST for {0}\n".format(path_test))

    # display all tests
    for i, s in enumerate(suite):
        if skip >= 0 and i < skip:
            continue
        if i + 1 in skip_list:
            continue
        cut = os.path.split(s[1])
        cut = os.path.split(cut[0])[-1] + "/" + cut[-1]
        if skip_function is not None:
            with open(s[1], "r") as f:
                content = f.read()
            if skip_function(s[1], content, duration.get(cut, None)):
                continue

        if cut not in duration:
            raise Exception("{0} not found in\n{1}".format(
                cut, "\n".join(sorted(duration.keys()))))
        else:
            dur = duration[cut]
        zzz = "\ntest % 3d (%04ds), %s" % (i + 1, dur, cut)
        memout.write(zzz)
    memout.write("\n")

    # displays
    memout.write("---- RUN UT\n")

    # run all tests
    for i, s in enumerate(suite):
        if skip >= 0 and i < skip:
            continue
        if i + 1 in skip_list:
            continue
        cut = os.path.split(s[1])
        cut = os.path.split(cut[0])[-1] + "/" + cut[-1]
        if skip_function is not None:
            with open(s[1], "r") as f:
                content = f.read()
            if skip_function(s[1], content, duration.get(cut, None)):
                continue

        zzz = "running test % 3d, %s" % (i + 1, cut)
        zzz += (60 - len(zzz)) * " "
        memout.write(zzz)

        if log and fLOG is not print:
            fLOG(OutputPrint=True)
            fLOG(Lock=True)

        newstdr = StringIO()
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
                fLOG("running")
                r = runner.run(s[0])
                out = r.stream.getvalue()
                fLOG("end running")

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
            try:
                memout.write(err)
            except UnicodeDecodeError:
                err_e = err.decode("ascii", errors="ignore")
                memout.write(err_e)
            except UnicodeEncodeError:
                try:
                    err_e = err.encode("ascii", errors="ignore")
                    memout.write(err_e)
                except TypeError:
                    err_e = err.encode("ascii", errors="ignore").decode(
                        'ascii', errors='ingore')
                    memout.write(err_e)

            fail += 1

            fullstderr.write("\n#-----" + lis[i] + "\n")
            fullstderr.write("OUT:\n")
            fullstderr.write(out)

            if err:
                fullstderr.write("ERRo:\n")
                try:
                    fullstderr.write(err)
                except UnicodeDecodeError:
                    err_e = err.decode("ascii", errors="ignore")
                    fullstderr.write(err_e)
                except UnicodeEncodeError:
                    err_e = err.encode("ascii", errors="ignore")
                    fullstderr.write(err_e)

            if len(list_warn) > 0:
                fullstderr.write("WARN:\n")
                warndone = set()
                for w in list_warn:
                    if filter_warning(w):
                        sw = str(w)
                        if sw not in warndone:
                            # we display only one time the same warning
                            fullstderr.write("w{0}: {1}\n".format(i, str(w)))
                            warndone.add(sw)
            serr = newstdr.getvalue()
            if serr.strip(" \n\r\t"):
                fullstderr.write("ERRs:\n")
                fullstderr.write(serr)
        else:
            allwarn.append((lis[i], list_warn))
            val = newstdr.getvalue()
            if len(val) > 0 and is_valid_error(val):
                fullstderr.write("\n*-----" + lis[i] + "\n")
                if len(list_warn) > 0:
                    fullstderr.write("WARN:\n")
                    for w in list_warn:
                        if filter_warning(w):
                            fullstderr.write("w{0}: {1}\n".format(i, str(w)))
                if val.strip(" \n\r\t"):
                    fullstderr.write("ERRv:\n")
                    fullstderr.write(val)

        memout.write("\n")

        keep.append((s[1], r))

    # displays
    memout.write("---- END UT\n")

    # end, catch standard output and err
    sys.stderr = memo_stderr
    sys.stdout = memo_stdout
    val = fullstderr.getvalue()

    if len(val) > 0:
        flogp("-- STDERR (from unittests) on STDOUT")
        flogp(val)
        flogp("-- end STDERR on STDOUT")

        if on_stderr:
            memerr.write("##### STDERR (from unittests) #####\n")
            memerr.write(val)
            memerr.write("##### end STDERR #####\n")

    if fail == 0:
        clean()

    for fi, lw in allwarn:
        if len(lw) > 0:
            memout.write("WARN: {0}\n".format(fi))
            for i, w in enumerate(lw):
                if filter_warning(w):
                    try:
                        sw = "  w{0}: {1}\n".format(i, w)
                    except UnicodeEncodeError:
                        sw = "  w{0}: Unable to convert a warnings of type {0} into a string (1)".format(
                            i, type(w))
                    try:
                        memout.write(sw)
                    except UnicodeEncodeError:
                        sw = "  w{0}: Unable to convert a warnings of type {0} into a string (2)".format(
                            i, type(w))
                        memout.write(sw)

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


def default_skip_function(name, code, duration):
    """
    default skip function for function @see fn main_wrapper_tests.

    @param      name        name of the test file
    @param      code        code of the test file
    @param      duration    estimated duration of the tests (specified in the file documentation)
    @return                 True if skipped, False otherwise
    """
    if "test_SKIP_" in name or "test_LONG_" in name or "test_GUI_" in name:
        return True
    return False
