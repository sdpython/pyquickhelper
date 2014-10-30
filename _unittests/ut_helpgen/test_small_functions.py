"""
@brief      test log(time=8s)
@author     Xavier Dupre
"""

import sys, os, unittest, shutil


try :
    import src
except ImportError :
    path =  os.path.normpath(os.path.abspath(os.path.join(os.path.split(__file__)[0], "..", "..")))
    if path not in sys.path : sys.path.append(path)
    import src
    
from src.pyquickhelper.loghelper.flog           import fLOG
from src.pyquickhelper.helpgen.utils_sphinx_doc_helpers import make_label_index

class TestSmallFunction(unittest.TestCase):
    
    def test_make_label_index(self) :
        fLOG (__file__, self._testMethodName, OutputPrint = __name__ == "__main__")
        title = "abAB_-()56$?"
        res = make_label_index(title,"")
        fLOG("***",title,res)
        assert res == "abAB_-56"
        
if __name__ == "__main__"  :
    unittest.main ()    
