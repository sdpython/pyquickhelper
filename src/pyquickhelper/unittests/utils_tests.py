"""
@file
@brief  This extension contains various functionalities to help unittesting.
"""
import os, sys, glob, re, unittest, io

from ..sync.synchelper      import remove_folder
from ..loghelper.flog       import fLOG


def get_test_file (filter, dir = None) :
    """
    return the list of test files
    @param      dir         path to look (or paths to look if it is a list)
    @param      filter      only select files matching the pattern (ex: test*)
    @return                 a list of test files
    """

    if dir is None :
        path = os.path.split(__file__)[0]
        nrt  = os.path.abspath(os.path.join(path, "..", "..", "_nrt"))
        uts  = os.path.abspath(os.path.join(path, "..", "..", "_unittest"))
        ut2  = os.path.abspath(os.path.join(path, "..", "..", "_unittests"))
        dirs = [ nrt, uts, ut2 ]
    elif isinstance(dir, str) :
        if not os.path.exists(dir) :
            raise FileNotFoundError (dir)
        dirs = [ dir ]
    else :
        dirs = dir
        for d in dirs :
            if not os.path.exists(d) :
                raise FileNotFoundError (d)

    copypaths = sys.path.copy()

    li   = [ ]
    for dir in dirs :
        if "__pycache__" in dir : continue
        if not os.path.exists (dir) :
            continue
        if dir not in sys.path and dir != "." :
            sys.path.append (dir)
        li += glob.glob (dir + "/" + filter)
        if filter != "temp_*" :
            li = [ l for l in li if "test_" in l and ".py" in l and \
                                    "test_main" not in l and \
                                    "temp_" not in l and \
                                    "out.test_copyfile.py.2.txt" not in l and \
                                    ".pyc" not in l and \
                                    ".pyd" not in l and \
                                    ".so" not in l and \
                                    ".py~" not in l and \
                                    ".pyo" not in l ]

        lid = glob.glob (dir + "/*")
        for l in lid :
            if os.path.isdir (l) :
                temp = get_test_file (filter, l)
                temp = [t for t in temp ]
                li.extend (temp)

    # we restore sys.path
    sys.path = copypaths

    return li

def get_estimation_time (file) :
    """
    return an estimation of the processing time, it extracts the number in ``(time=5s)`` for example

    @param      file        filename
    @return                 int
    """
    try :
        f = open (file, "r")
        li = f.readlines ()
        f.close ()
    except UnicodeDecodeError :
        try :
            f = open (file, "r", encoding="latin-1")
            li = f.readlines ()
            f.close ()
        except Exception as ee :
            raise Exception("issue with %s\n%s" % (file,str(ee)))

    s = ''.join (li)
    c = re.compile ("[(]time=([0-9]+)s[)]").search (s)
    if c is None : return 0
    else : return int (c.groups () [0])

def import_files (li) :
    """
    run all tests in file list li

    @param      li      list of files (python scripts)
    @return             list of tests [ ( testsuite, file) ]
    """
    allsuite = []
    for l in li :

        copypath = sys.path.copy()

        sdir = os.path.split (l) [0]
        if sdir not in sys.path :
            sys.path.append (sdir)
        tl  = os.path.split (l) [1]
        fi  = tl.replace (".py", "")

        if fi in ["neural_network", "test_c",
                  "test_model", "test_look_up",
                  "test_look_up.extract.txt"] :
            try :
                mo = __import__ (fi)
            except Exception as e :
                print ("unable to import ", fi)
                mo = None
        else :
            try :
                mo = __import__ (fi)
            except :
                print ("problem with ",fi)
                mo = __import__ (fi)

        # some tests can mess up with the import path
        sys.path = copypath

        cl = dir (mo)
        for c in cl :
            if len (c) < 5 or c [:4] != "Test" : continue
            # test class c
            testsuite = unittest.TestSuite ()
            loc = locals()
            exec (compile ("di = dir (mo." + c + ")", "", "exec"), globals(), loc)
            di = loc["di"]
            for d in di :
                if len (d) >= 6 and d [:5] == "_test" :
                    raise RuntimeError ("a function _test is still deactivated %s in %s" % (d, c))
                if len (d) < 5 or d [:4] != "test" : continue
                # method d.c
                loc = locals()
                exec (compile ("t = mo." + c + "(\"" + d + "\")", "", "exec"), globals(), loc)
                t = loc["t"]
                testsuite.addTest (t)
            allsuite.append ((testsuite, l))

    return allsuite

def clean () :
    """
    do the cleaning
    """
    # do not use SVN here just in case some files are not checked in.
    print()
    for log_file in ["temp_hal_log.txt", "temp_hal_log2.txt",
                    "temp_hal_log_.txt", "temp_log.txt", "temp_log2.txt", ] :
        li = get_test_file (log_file)
        for l in li :
            try :
                if os.path.isfile (l) : os.remove (l)
            except Exception as e :
                print ("unable to remove file",l, " --- ", str(e).replace("\n", " "))

    li = get_test_file ("temp_*")
    for l in li :
        try :
            if os.path.isfile (l) : os.remove (l)
        except Exception as e :
            print ("unable to remove file. ",l, " --- ", str(e).replace("\n", " "))
    for l in li :
        try :
            if os.path.isdir (l) :
                remove_folder (l)
        except Exception as e :
            print ("unable to remove dir. ",l, " --- ", str(e).replace("\n", " "))

def main (  runner,
            path_test   = None,
            limit_max   = 1e9,
            log         = False,
            skip        = -1,
            on_stderr   = False,
            flogp       = print) :
    """
    run all unit test
    the function looks into the folder _unittest and extract from all files
    beginning by `test_` all methods starting by `test_`.
    Each files should mention an execution time.
    Tests are sorted by increasing order.

    @param      runner      unittest Runner
    @param      path_test   path to look, if None, looks for defaults path related to this project
    @param      limit_max   avoid running tests longer than limit seconds
    @param      log         if True, enables intermediate files
    @param      skip        if skip != -1, skip the first "skip" test files
    @param      on_stderr   if True, publish everything on stderr at the end
    @param      flogp       logging, printing function
    @return                 dictionnary: ``{ "err": err, "tests":list of couple (file, test results) }``

    .. versionchanged:: 0.9
        change the result type into a dictionary
    """

    # checking that the module does not belong to the installed modules
    if path_test is not None :
        path_module = os.path.join(sys.executable, "Lib", "site-packages")
        paths = [ os.path.join(path_module, "src"), ]
        for path in paths :
            if os.path.exists (path):
                raise FileExistsError("this path should not exist " + path)

    li      = get_test_file ("test*", path_test)
    est     = [ get_estimation_time(l) for l in li ]
    co      = [ (e,l) for e,l in zip(est, li) ]
    co.sort ()
    cco     = []

    if skip != -1 : flogp ("found ", len(co), " test files skipping", skip)
    else :          flogp ("found ", len(co), " test files")

    index   = 0
    for e,l in co:
        if e > limit_max :
            continue
        cut = os.path.split(l)
        cut = os.path.split(cut[0])[-1] + "/" + cut[-1]
        if skip == -1 or index >= skip :
            flogp ("% 3d - time " % (len(cco)+1), "% 3d" % e, "s  --> ", cut)
        cco.append( (e, l) )
        index += 1

    exp = re.compile ("Ran ([0-9]+) tests? in ([.0-9]+)s")

    li      = [ a [1] for a in cco ]
    lis     = [ os.path.split(_)[-1] for _ in li ]
    suite   = import_files (li)
    keep    = []
    #memerr  = sys.stderr
    memout  = sys.stdout
    fail    = 0

    stderr      = sys.stderr
    fullstderr  = io.StringIO()

    for i,s in enumerate(suite) :
        if skip >= 0 and i < skip :
            continue

        cut = os.path.split(s[1])
        cut = os.path.split(cut[0])[-1] + "/" + cut[-1]
        zzz = "running test % 3d, %s" % (i+1,cut)
        zzz += (60 - len (zzz)) * " "
        memout.write (zzz)

        if log :
            fLOG(OutputPrint=True)
            fLOG(Lock=True)

        newstdr     = io.StringIO()
        keepstdr    = sys.stderr
        sys.stderr  = newstdr

        r   = runner.run(s[0])
        out = r.stream.getvalue ()
        ti  = exp.findall (out) [-1]
        add = " ran %s tests in %ss" % ti  # don't modify it, PyCharm does not get it right (ti is a tuple)

        sys.stderr  = keepstdr

        if log :
            fLOG(Lock=False)

        memout.write (add)

        if not r.wasSuccessful() :
            err = out.split ("===========")
            err = err [-1]
            memout.write ("\n")
            memout.write (err)
            fail += 1

            fullstderr.write("\n#-----" + lis[i] + "\n")
            fullstderr.write("OUT:\n")
            fullstderr.write(out)
            fullstderr.write("ERRo:\n")
            fullstderr.write(err)
            fullstderr.write("ERR:\n")
            fullstderr.write(newstdr.getvalue())
        else:
            val = newstdr.getvalue()
            if len(val) > 0 and is_valid_error(val) :
                fullstderr.write("\n*-----" + lis[i] + "\n")
                fullstderr.write("ERR:\n")
                fullstderr.write(val)

        memout.write ("\n")

        keep.append( (s[1], r) )

    sys.stderr = stderr
    sys.stdout = memout
    val = fullstderr.getvalue()

    if len(val) > 0 :
        flogp ("-- STDERR (from unittests) on STDOUT")
        flogp (val)
        flogp ("-- end STDERR on STDOUT")

        if on_stderr :
            sys.stderr.write("##### STDERR (from unittests) #####\n")
            sys.stderr.write(val)
            sys.stderr.write("##### end STDERR #####\n")

    if fail == 0 :
        clean ()

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
    keys  = ["Exception", "Error", "TraceBack", "invalid", " line "]
    error = error.lower()
    for key in keys:
        if key.lower() in error:
            return True
    return False