"""
@brief      test tree node (time=5s)
"""


from __future__ import print_function
import sys, os, unittest

try :
    import src
except ImportError :
    path = os.path.normpath(os.path.abspath( os.path.join( os.path.split(__file__)[0], "..", "..")))
    if path not in sys.path : sys.path.append (path)
    import src

try :
    import pymyinstall
except ImportError :
    path = os.path.normpath(os.path.abspath( os.path.join( os.path.split(__file__)[0], "..", "..", "..", "pymyinstall", "src")))
    if path not in sys.path : sys.path.append (path)
    import pymyinstall

from src.pyquickhelper.loghelper.flog        import fLOG
from src.pyquickhelper.sync.visual_sync      import create_visual_diff_through_html

class TestJsDiffLib(unittest.TestCase):
    
    def test_jsdifflib(self) :
        fLOG (__file__, self._testMethodName, OutputPrint = __name__ == "__main__")
        tt = os.path.split(src.pyquickhelper.sync.visual_sync.__file__)[0]
        ma = os.path.join(tt, "temp_difflibjs", "jsdifflib-master")
        if os.path.exists(ma):
            for i in os.listdir(ma) :
                os.remove(os.path.join(ma,i))
        assert not os.path.exists(os.path.join(ma,"difflib.js"))
        p = create_visual_diff_through_html("a","b")
        assert len(p) > 0
        assert os.path.exists(os.path.join(ma,"difflib.js"))
        

if __name__ == "__main__"  :
    unittest.main ()    
