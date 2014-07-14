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
from src.pyquickhelper.helpgen.sphinx_main      import post_process_rst_output

class TestRst(unittest.TestCase):
    
    def test_rst(self) :
        fLOG (__file__, self._testMethodName, OutputPrint = __name__ == "__main__")
        path = os.path.abspath(os.path.split(__file__)[0])
        file = os.path.join(path, "data", "td1a_cenonce_session_10.rst")
        temp = os.path.join(path,"temp_rst")
        if not os.path.exists(temp) : os.mkdir(temp)
        dest = os.path.join(temp, os.path.split(file)[-1])
        if os.path.exists(dest) : os.remove(dest)
        shutil.copy(file,temp)
        post_process_rst_output(dest, False, False, False)
        
        
if __name__ == "__main__"  :
    unittest.main ()    
