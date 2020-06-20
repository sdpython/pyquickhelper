"""
@file
@brief This extension contains various functionalities to help unittesting.
"""
import os
import sys
import glob
import re
import unittest
import warnings
from io import StringIO
from .utils_tests_stringio import StringIOAndFile
from .default_filter_warning import default_filter_warning
from ..filehelper.synchelper import remove_folder
from ..loghelper.flog import run_cmd, noLOG


def get_test_file(filter, folder=None, no_subfolder=False, fLOG=noLOG, root=None):
    """
    Returns the list of test files.

    @param      folder          path to look (or paths to look if it is a list)
    @param      filter          only select files matching the pattern (ex: test*)
    @param      no_subfolder    the function investigates the folder *folder* and does not try any subfolder in
                                ``{"_nrt", "_unittest", "_unittests"}``
    @param      fLOG            logging function
    @param      root            root or folder which contains the project,
                                rules applyong on folder name will not apply on it
    @return                     a list of test files
    """
    if no_subfolder:
        dirs = [folder]
    else:
        expected = {"_nrt", "_unittest", "_unittests"}
        if folder is None:
            path = os.path.split(__file__)[0]
            dirs = [os.path.join(path, "..", "..", d) for d in expected]
        elif isinstance(folder, str):
            if not os.path.exists(folder):
                raise FileNotFoundError(folder)  # pragma: no cover
            last = os.path.split(folder)[-1]
            if last in expected:
                dirs = [folder]
            else:
                dirs = [os.path.join(folder, d) for d in expected]
        else:
            dirs = folder
            for d in dirs:
                if not os.path.exists(d):
                    raise FileNotFoundError(d)

    copypaths = list(sys.path)

    li = []
    for fold in dirs:
        if "__pycache__" in fold or "site-packages" in fold:
            continue
        if not os.path.exists(fold):
            continue
        if fold not in sys.path and fold != ".":
            sys.path.append(fold)
        content = glob.glob(fold + "/" + filter)
        if filter != "temp_*":
            if root is not None:
                def remove_root(p):
                    if p.startswith(root):
                        return p[len(root):]
                    return p
                couples = [(remove_root(il), il) for il in content]
            else:
                couples = [(il, il) for il in content]

            content = []
            for il, fu in couples:
                if "test_" in il and ".py" in il and ".py.err" not in il and \
                    ".py.out" not in il and ".py.warn" not in il and \
                    "test_main" not in il and "temp_" not in il and \
                    "temp2_" not in il and ".pyo" not in il and \
                    "out.test_copyfile.py.2.txt" not in il and \
                    ".pyc" not in il and ".pyd" not in il and \
                        ".so" not in il and ".py~" not in il:
                    content.append(fu)
        li.extend(content)
        fLOG("[get_test_file], inspecting", dirs)

        lid = glob.glob(fold + "/*")
        for il in lid:
            if os.path.isdir(il):
                temp = get_test_file(
                    filter, il, no_subfolder=True, fLOG=fLOG, root=root)
                temp = list(temp)
                li.extend(temp)

    # we restore sys.path
    sys.path = copypaths

    return li


def get_estimation_time(file):
    """
    Return an estimation of the processing time,
    it extracts the number in ``(time=5s)`` for example.

    @param      file        filename
    @return                 int
    """
    try:
        f = open(file, "r", errors="ignore")
        li = f.readlines()
        f.close()
    except Exception as e:  # pragma: no cover
        warnings.warn("Issue with '{0}'\n{1}\n{2}".format(
            file, type(e), e), UserWarning)
        return 10
    try:
        s = ''.join(li)
    except Exception as e:  # pragma: no cover
        warnings.warn(
            "Probably an enconding issue for file '{0}'\n{1}\n{2}".format(
                file, type(e), e), UserWarning)
        return 10
    c = re.compile("[(]time=([0-9]+)s[)]").search(s)
    if c is None:
        return 0
    return int(c.groups()[0])


def import_files(li, additional_ut_path=None, fLOG=noLOG):
    """
    Runs all tests in file list ``li``.

    @param      li                      list of files (python scripts)
    @param      additional_ut_path      additional paths to add when running the unit tests
    @param      fLOG                    logging function
    @return                             list of tests [ ( testsuite, file) ]
    """
    allsuite = []
    for le in li:

        copypath = list(sys.path)

        sdir = os.path.split(le)[0]
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
        tl = os.path.split(le)[1]
        fi = tl.replace(".py", "")

        try:
            mo = __import__(fi)
        except Exception as e:  # pragma: no cover
            raise ImportError("Unable to import '{}' due to {}.\nsys.path=\n{}".format(
                fi, e, "\n".join(sys.path)))

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
                    raise RuntimeError(  # pragma: no cover
                        "a function _test is still deactivated %s in %s" % (d, c))
                if len(d) < 5 or d[:4] != "test":
                    continue
                # method d.c
                loc = locals()
                code = "t = mo." + c + "(\"" + d + "\")"
                cp = compile(code, "", "exec")
                try:
                    exec(cp, globals(), loc)
                except Exception as e:
                    raise Exception(  # pragma: no cover
                        "Unable to execute code '{0}'".format(code)) from e
                t = loc["t"]
                testsuite.addTest(t)

            allsuite.append((testsuite, le))

    return allsuite


def clean(folder=None, fLOG=noLOG):
    """
    Does the cleaning.

    @param      dir     directory
    @param      fLOG    logging function
    """
    # do not use SVN here just in case some files are not checked in.
    for log_file in ["temp_hal_log.txt", "temp_hal_log2.txt",
                     "temp_hal_log_.txt", "temp_log.txt", "temp_log2.txt", ]:
        li = get_test_file(log_file, folder=folder)
        for el in li:
            try:
                if os.path.isfile(el):
                    os.remove(el)
            except Exception as e:  # pragma: no cover
                fLOG("[clean] unable to remove file '{}' due to {}".format(
                    el, str(e).replace("\n", " ")))

    li = get_test_file("temp_*")
    for el in li:
        try:
            if os.path.isfile(el):
                os.remove(el)
        except Exception as e:  # pragma: no cover
            fLOG("[clean] unable to remove file '{}' due to {}".format(
                el, str(e).replace("\n", " ")))
    for el in li:
        try:
            if os.path.isdir(el):
                remove_folder(el)
        except Exception as e:  # pragma: no cover
            fLOG("[clean] unable to remove dir '{}' due to {}".format(
                el, str(e).replace("\n", " ")))


def main_run_test(runner, path_test=None, limit_max=1e9, log=False, skip=-1, skip_list=None,
                  on_stderr=False, processes=False, skip_function=None,
                  additional_ut_path=None, stdout=None, stderr=None, filter_warning=None,
                  fLOG=noLOG):
    """
    Runs all unit tests,
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
    @param      processes           to run the unit test in a separate process (with function @see fn run_cmd),
                                    however, to make that happen, you need to specify
                                    ``exit=False`` for each test file, see `unittest.main
                                    <https://docs.python.org/3/library/unittest.html#unittest.main>`_
    @param      additional_ut_path  additional paths to add when running the unit tests
    @param      stdout              if not None, use this stream instead of *sys.stdout*
    @param      stderr              if not None, use this stream instead of *sys.stderr*
    @param      filter_warning      function which removes some warnings in the final output,
                                    if None, the function filters out some recurrent warnings
                                    in jupyter (signature: ``def filter_warning(w: warning) -> bool``),
                                    @see fn default_filter_warning
    @param      fLOG                logging function
    @return                         dictionnary: ``{ "err": err, "tests":list of couple (file, test results) }``
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
                raise FileExistsError(  # pragma: no cover
                    "This path should not exist '{}'.".format(path))

    def short_name(el):
        cut = os.path.split(el)
        cut = os.path.split(cut[0])[-1] + "/" + cut[-1]
        return cut

    # sort the test by increasing expected time
    fLOG("[main_run_test] path_test", path_test)
    li = get_test_file("test*", folder=path_test, fLOG=fLOG, root=path_test)
    if len(li) == 0:
        raise FileNotFoundError("no test files in " + path_test)
    est = [get_estimation_time(el) for el in li]
    co = [(e, short_name(el), el) for e, el in zip(est, li)]
    co.sort()

    # we check we do not run twice the same file
    done = {}
    duplicate = []
    for _, cut, lc in co:
        if cut in done:
            duplicate.append((cut, lc))
        done[cut] = True

    if len(duplicate) > 0:  # pragma: no cover
        s = list(set(duplicate))
        s.sort()
        mes = "\n".join(str(_) for _ in s)
        raise Exception("duplicated test file were detected:\n" + mes)

    # check existing
    if len(co) == 0:
        raise FileNotFoundError(  # pragma: no cover
            "unable to find any test files in {0}".format(path_test))

    if skip != -1:
        fLOG("[main_run_test] found ", len(co), " test files skipping", skip)
    else:
        fLOG("[main_run_test] found ", len(co), " test files")

    # extract the test classes
    cco = []
    duration = {}
    index = 0
    for e, cut, l in co:
        if e > limit_max:
            continue  # pragma: no cover
        cco.append((e, l))
        cut = os.path.split(l)
        cut = os.path.split(cut[0])[-1] + "/" + cut[-1]
        duration[cut] = e
        index += 1

    exp = re.compile("Ran ([0-9]+) tests? in ([.0-9]+)s")

    # run the test
    li = [a[1] for a in cco]
    suite = import_files(li, additional_ut_path=additional_ut_path, fLOG=fLOG)
    lis = [os.path.split(name)[-1] for _, name in suite]
    keep = []

    # redirect standard output, error
    fLOG("[main_run_test] redirect stdout, stderr")
    memo_stdout = sys.stdout
    memout = sys.stdout if stdout is None else stdout
    fail = 0
    allwarn = []

    memo_stderr = sys.stderr
    memerr = sys.stderr if stderr is None else stderr
    fullstderr = StringIO()

    # displays
    memout.write("[main_run_test] ---- JENKINS BEGIN UNIT TESTS ----")
    memout.write(
        "[main_run_test] ---- BEGIN UNIT TEST for {0}\n".format(path_test))

    # display all tests
    for i, s in enumerate(suite):
        if skip >= 0 and i < skip:
            continue  # pragma: no cover
        if i + 1 in skip_list:
            continue  # pragma: no cover
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
        dur = duration[cut]
        zzz = "\ntest % 3d (%04ds), %s" % (i + 1, dur, cut)
        memout.write(zzz)
    memout.write("\n")

    # displays
    memout.write("[main_run_test] ---- RUN UT\n")
    original_stream = runner.stream.stream if isinstance(
        runner.stream.stream, StringIOAndFile) else None

    # run all tests
    last_s = None
    for i, s in enumerate(suite):
        last_s = s
        if skip >= 0 and i < skip:
            continue  # pragma: no cover
        if i + 1 in skip_list:
            continue  # pragma: no cover
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

        # the errors are logged into a file just beside the test file
        newstdr = StringIOAndFile(s[1] + ".err")
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
                    if original_stream is not None:
                        original_stream.begin_test(s[1])
                    r = runner.run(s[0])
                    out = r.stream.getvalue()
                    if original_stream is not None:
                        original_stream.end_test(s[1])
                    for ww in w:
                        list_warn.append((ww, s))
            else:
                if original_stream is not None:
                    original_stream.begin_test(s[1])
                r = runner.run(s[0])
                out = r.stream.getvalue()
                if original_stream is not None:
                    original_stream.end_test(s[1])

        ti = exp.findall(out)[-1]
        # don't modify it, PyCharm does not get it right (ti is a tuple)
        add = " ran %s tests in %ss" % ti

        sys.stderr = keepstdr

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

            # stores the output in case of an error
            with open(s[1] + ".err", "w", encoding="utf-8", errors="ignore") as f:
                f.write(out)

            fail += 1

            fullstderr.write("\n#-----" + lis[i] + "\n")
            fullstderr.write("OUT:\n")
            fullstderr.write(out)

            if err:
                fullstderr.write("[pyqerror]o:\n")
                try:
                    fullstderr.write(err)
                except UnicodeDecodeError:
                    err_e = err.decode("ascii", errors="ignore")
                    fullstderr.write(err_e)
                except UnicodeEncodeError:
                    err_e = err.encode("ascii", errors="ignore")
                    fullstderr.write(err_e)

            list_warn = [(w, s) for w, s in list_warn if filter_warning(w)]
            if len(list_warn) > 0:
                fullstderr.write("*[pyqwarning]:\n")
                warndone = set()
                for w, slw in list_warn:
                    sw = str(slw)
                    if sw not in warndone:
                        # we display only one time the same warning
                        fullstderr.write("w{0}: {1}\n".format(i, sw))
                        warndone.add(sw)
            serr = newstdr.getvalue()
            if serr.strip(" \n\r\t"):
                fullstderr.write("ERRs:\n")
                fullstderr.write(serr)
        else:
            list_warn = [(w, s) for w, s in list_warn if filter_warning(w)]
            allwarn.append((lis[i], list_warn))
            val = newstdr.getvalue()
            if val.strip(" \n\r\t"):
                # Remove most of the Sphinx warnings (sphinx < 1.8)
                lines = val.strip(" \n\r\t").split("\n")
                lines = [
                    _ for _ in lines if _ and "is already registered, it will be overridden" not in _]
                val = "\n".join(lines)
            if len(val) > 0 and is_valid_error(val):
                fullstderr.write("\n*-----" + lis[i] + "\n")
                if len(list_warn) > 0:
                    fullstderr.write("[main_run_test] +WARN:\n")
                    for w, _ in list_warn:
                        fullstderr.write(
                            "[in:{2}] w{0}: {1}\n".format(i, str(w), cut))
                if val.strip(" \n\r\t"):
                    fullstderr.write("[in:{0}] ERRv:\n".format(cut))
                    fullstderr.write(val)

        memout.write("\n")
        keep.append((last_s[1], r))

    # displays
    memout.write("[main_run_test] ---- END UT\n")
    memout.write("[main_run_test] ---- JENKINS END UNIT TESTS ----\n")

    fLOG("[main_run_test] restore stdout, stderr")

    # end, catch standard output and err
    sys.stderr = memo_stderr
    sys.stdout = memo_stdout
    val = fullstderr.getvalue()

    if len(val) > 0:
        fLOG("[main_run_test] -- STDERR (from unittests) on STDOUT")
        fLOG(val)
        fLOG("[main_run_test] -- end STDERR on STDOUT")

        if on_stderr:
            memerr.write(
                "[main_run_test] ##### STDERR (from unittests) #####\n")
            memerr.write(val)
            memerr.write("[main_run_test] ##### end STDERR #####\n")

    if fail == 0:
        clean(fLOG=fLOG)

    fLOG("[main_run_test] printing warnings")

    for fi, lw in allwarn:
        if len(lw) > 0:
            memout.write("[main_run_test] -WARN: {0}\n".format(fi))
            wdone = {}
            for i, (w, s) in enumerate(lw):
                sw = str(w)
                if sw in wdone:
                    continue
                wdone[sw] = w
                try:
                    sw = "  w{0}: {1}\n".format(i, w)
                except UnicodeEncodeError:  # pragma: no cover
                    sw = "  w{0}: Unable to convert a warnings of type {1} into a string (1)".format(
                        i, type(w))
                try:
                    memout.write(sw)
                except UnicodeEncodeError:  # pragma: no cover
                    sw = "  w{0}: Unable to convert a warnings of type {1} into a string (2)".format(
                        i, type(w))
                    memout.write(sw)

    fLOG("[main_run_test] END of unit tests")
    memout.write("[main_run_test] END of unit tests\n")

    return dict(err=val, tests=keep)


def is_valid_error(error):
    """
    Checks if the text written on stderr is an error or not,
    a local server can push logs on this stream,
    it looks for keywords such as ``Exception``,
    ``Error``, ``TraceBack``...

    @param      error       text
    @return                 boolean
    """
    lines = error.split('\n')
    lines = [
        line for line in lines if "No module named 'numpy.core._multiarray_umath'" not in line]
    error = "\n".join(lines)
    keys = ["Exception", "Error", "TraceBack", "invalid", " line "]
    error = error.lower()
    for key in keys:
        if key.lower() in error:
            return True
    return False


def default_skip_function(name, code, duration):
    """
    Default skip function for function @see fn main_wrapper_tests.

    @param      name        name of the test file
    @param      code        code of the test file
    @param      duration    estimated duration of the tests (specified in the file documentation)
    @return                 True if skipped, False otherwise
    """
    if "test_SKIP_" in name or "test_LONG_" in name or "test_GUI_" in name:
        return True
    return False
