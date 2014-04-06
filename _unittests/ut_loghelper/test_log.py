"""
@brief      test log(time=0s)
"""

import sys, os, unittest


try :
    import src
except ImportError :
    path = os.path.normpath(os.path.abspath( os.path.join( os.path.split(__file__)[0], "..", "..")))
    if path not in sys.path : sys.path.append (path)
    import src

from src.pyquickhelper.loghelper.flog import fLOG, run_cmd, load_content_file_with_encoding, run_script, get_prefix, removedirs, unzip, guess_type_list


class TestLog (unittest.TestCase):
    
    def test_random_curve (self) :
        fLOG (__file__, self._testMethodName, OutputPrint = __name__ == "__main__")
        fLOG ("message", "ok", option1 = "k", option2 = 2)
        assert os.path.exists ("temp_log.txt")
        #os.remove ("hal_log.txt")
        
    def test_import_problem (self) :
        fLOG (__file__, self._testMethodName, OutputPrint = __name__ == "__main__")
        for k in sys.modules :
            if k == "core.codecs" :
                if __name__ == "__main__" :
                    keys = sys.modules.keys ()
                    keys.sort ()
                    for k in keys :
                        if sys.modules [k] == None :
                            print ("None ", k)
                #raise Exception ("shit")        
                
    def test_cmd (self) :
        fLOG (__file__, self._testMethodName, OutputPrint = __name__ == "__main__")
        out,err = run_cmd ("dir", shell = True, wait = True)
        assert len (out) > 0
        out,err = run_cmd ("dir *.pyc", shell = True, wait = True)
        assert len (out) > 0

    def test_cmd_communicate (self) :
        fLOG (__file__, self._testMethodName, OutputPrint = __name__ == "__main__")
        out,err = run_cmd ("dir *.py", shell = True, wait = True, communicate = True)
        assert len (out) > 0

    def test_python (self) :
        fLOG (__file__, self._testMethodName, OutputPrint = __name__ == "__main__")
        file = os.path.join (os.path.split (__file__)[0], "..", "..", "src", "pyquickhelper", "loghelper", "flog.py")
        out,err = run_script (file)
        assert len (out) == 0
        assert len (err) == 0
        
    def test_prefix (self) :
        fLOG (__file__, self._testMethodName, OutputPrint = __name__ == "__main__")
        p1 = get_prefix ()
        p2 = get_prefix ()
        assert p1 != p2
        
    def test_unzip (self) :
        pat  = os.path.abspath(os.path.join (os.path.split (__file__) [0], "temp_zip22"))
        patl = os.path.abspath(os.path.join (os.path.split (__file__) [0], "temp_zip22log"))
        fLOG (__file__, self._testMethodName, OutputPrint = __name__ == "__main__", LogPath = patl)
        if not os.path.exists(pat): os.mkdir(pat)
        
        z   = os.path.abspath(os.path.join (os.path.split (__file__) [0], "data", "test_file_nrt.zip"))
        unz = unzip (z, path_unzip = pat)
        assert os.path.exists (os.path.join (pat, "test_file_nrt.txt"))
        unz = unzip (z, path_unzip = pat)
        
        z   = os.path.abspath(os.path.join (os.path.split (__file__) [0], "data", "test_log_nrt.gz"))
        unz = unzip (z, path_unzip = pat)
        assert os.path.exists (os.path.join (pat, "test_log_nrt.txt"))
        unz = unzip (z, path_unzip = pat)

        fLOG("A")
        z   = os.path.abspath(os.path.join (os.path.split (__file__) [0], "data", "sample_zip.zip"))
        unz = unzip (z, path_unzip = pat)

        fLOG("B")
        f   = os.path.join (pat, "tsv_error__.txt")
        if not os.path.exists (f): raise FileNotFoundError(f)
        f   = os.path.join (pat, "tsv_file__.txt")
        if not os.path.exists (f): raise FileNotFoundError(f)

        fLOG("C ** ",z)
        unz = unzip (z, path_unzip = pat)
        fLOG("***",unz)
        assert len(unz)>0

        fLOG("D")
        r = removedirs (pat, silent = True)
        if len (r) > 1 :
            raise Exception("pattern: " + pat + "\n" + "\n".join(r))
        
    def test_guess_type (self) :
        fLOG (__file__, self._testMethodName, OutputPrint = __name__ == "__main__")
        l   = ['0002', '0003', '0001', '0', '0', '0', '0', '0', '', '0002', '0003', '0001', '0002', '0003', '0001', '0002', '0003', '0001', '0002', '0001', '0002', '0001']
        res = guess_type_list (l)
        fLOG (res)
        assert res == (str, 8)
        
    def test_load_content_file_with_encoding(self) :
        fLOG (__file__, self._testMethodName, OutputPrint = __name__ == "__main__")
        file = __file__.replace(".pyc",".py")
        cont, enc = load_content_file_with_encoding(file)
        assert len(file) > 0


if __name__ == "__main__"  :
    unittest.main ()    
