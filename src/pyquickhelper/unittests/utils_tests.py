"""
@file
@brief  This extension contains various functionalities to help unittesting.
"""
import hashlib, functools, os, sys, glob, re, unittest

from ..loghelper.flog       import fLOG
from ..sync.synchelper      import remove_folder



def get_test_file (filter, dir = None) :
    """
    return the list of test files
    @param      dir         path to look
    @param      filter      only select files matching the pattern (ex: test*)
    @return                 a list of test files
    """
    
    if dir == None :
        path = os.path.split(__file__)[0]
        nrt  = os.path.abspath(os.path.join(path, "..", "..", "_nrt"))
        uts  = os.path.abspath(os.path.join(path, "..", "..", "_unittest"))
        ut2  = os.path.abspath(os.path.join(path, "..", "..", "_unittests"))
        dirs = [ nrt, uts, ut2 ]
    else :
        if not os.path.exists(dir) :
            raise FileNotFoundError (dir)
        dirs = [ dir ]
    
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
    except UnicodeDecodeError as e :
        try :
            f = open (file, "r", encoding="latin-1")
            li = f.readlines ()
            f.close ()
        except Exception as ee :
            raise Exception("issue with %s\n%s" % (file,str(e)))
        
    s = ''.join (li)
    c = re.compile ("[(]time=([0-9]+)s[)]").search (s)
    if c == None : return 0
    else : return int (c.groups () [0])
        
def import_files (li) :        
    """
    run all tests in file list li
    
    @param      li      list of files (python scripts)
    @return             list of tests [ ( testsuite, file) ]
    """
    allsuite = []
    for l in li :
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
        else :
            try :
                mo = __import__ (fi)
            except :
                print ("problem with ",fi)
                mo = __import__ (fi)
                
            
        cl = dir (mo)
        for c in cl :
            if len (c) < 5 or c [:4] != "Test" : continue
            # classe de test c
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
    """do the cleaning"""
    # do not use SVN here just in case some files are not checked in.
    print
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
    #print ()
    path = os.path.split (__file__) [0]
    d    = os.path.join (path, "model")
    if os.path.exists (d) : os.rmdir (d)
    d    = os.path.join (path, "param")
    if os.path.exists (d) : os.rmdir (d)
    d    = os.path.join (path, "temp")
    if False :
        if "hal_python" in sys.modules :
            HAL = sys.modules ["hal_python"]
            HAL.End ()
        if os.path.exists (d) : 
            li = glob.glob (d + "/*.*")
            for l in li : os.remove (l)
            os.rmdir (d)
    
def main (  runner, 
            path_test   = None,
            limit_max   = 1e9, 
            log         = False,
            skip        = -1) :
    """
    @param      runner      unittest Runner
    @param      path_test   path to look, if None, looks for defaults paht related to this project
    @param      limit_max   avoid running tests longer than limit seconds
    @param      log         if True, enables intermediate files
    @param      skip        if skip != -1, skip the first "skip" test files
    @return                 list of couple (file, test results)
    run all NRT
    """

    # checking that the module does not belong to the installed modules
    if path_test != None :
        pathModule = os.path.join(sys.executable, "Lib", "site-packages")
        paths = [ os.path.join(pathModule, "srcpyhome"),
                  os.path.join(pathModule, "pyhome3"),
                  os.path.join(pathModule, "pyhome"), ]
        for path in paths : 
            if os.path.exists (path): 
                raise FileExistsError("this path should not exist " + path)
        
    li      = get_test_file ("test*", path_test)
    est     = [ get_estimation_time(l) for l in li ]
    co      = [ (e,l) for e,l in zip(est, li) ]
    co.sort ()
    cco     = []
    limit   = -1
    if skip != -1 :
        print ("found ", len(co), " test files skipping", skip)
    else :
        print ("found ", len(co), " test files")
    index   = 0
    for e,l in co:
        if e > limit_max : 
            continue
        cut = os.path.split(l)
        cut = os.path.split(cut[0])[-1] + "/" + cut[-1]
        if skip == -1 or index >= skip :
            print ("% 3d - time " % (len(cco)+1), 
                    "% 3d" % e, "s  --> ", 
                    cut)
        cco.append( (e, l) )
        index += 1
    print
        
    exp = re.compile ("Ran ([0-9]+) tests? in ([.0-9]+)s")
        
    li      = [ a [1] for a in cco ]
    suite   = import_files (li)
    keep    = []
    memerr  = sys.stderr
    memout  = sys.stdout
    fail    = 0
    
    stderr      = sys.stderr
    sys.stderr  = UnicodeStringIO()
    
    for i,s in enumerate(suite) :
        if skip >= 0 and i < skip :
            continue
        cut = os.path.split(s[1])
        cut = os.path.split(cut[0])[-1] + "/" + cut[-1]
        zzz = "running test % 3d, %s" % (i+1,cut)
        zzz += (60 - len (zzz)) * " "
        memout.write (zzz)
        
        if log :
            HalLOG(OutputPrint=True)
            HalLOG(Lock=True)
        
        r   = runner.run(s[0])
        out = r.stream.getvalue ()
        ti  = exp.findall (out) [-1]
        add = " ran %s tests in %ss" % ti
        
        if log :
            HalLOG(Lock=False)
        
        memout.write (add)
        
        if not r.wasSuccessful () :
            err = out.split ("===========")
            err = err [-1]
            memout.write ("\n")
            memout.write (err)
            fail += 1
        
        memout.write ("\n")
        
        keep.append( (s[1], r) )
        
    val = sys.stderr.getvalue()
    if len(val) > 0 :
        print ("-------------------------------\nstderr")
        print (val)
        
    sys.stderr = stderr
        
    if fail == 0 :
        clean ()
        
    return keep
    