"""
@brief      test log(time=1s)
"""
import os, sys, unittest

try :
    import src
except ImportError :
    path = os.path.normpath(os.path.abspath( os.path.join( os.path.split(__file__)[0], "..", "..")))
    if path not in sys.path : sys.path.append (path)
    import src
    
from src.pyquickhelper.loghelper.flog import fLOG
from src.pyquickhelper.funcwin.function_helper import extract_function_information
from src.pyquickhelper.funcwin.default_functions import file_grep


class TestFonctionHelper (unittest.TestCase):
    
    def test_fonction_info (self) :
        fLOG(__file__, self._testMethodName, OutputPrint = __name__ == "__main__")
        res = extract_function_information(file_grep)
        for k in sorted(res):
            fLOG(k,res[k])
        for k in sorted(res["param"]):
            fLOG("--",k,res["param"][k],"-",res["types"][k])
        assert res["types"]["file"] == str
        
if __name__ == "__main__"  :
    unittest.main ()    
