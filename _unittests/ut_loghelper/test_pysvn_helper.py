# coding: latin-1
"""
@brief      test log(time=3s)
"""


from __future__ import print_function
import sys, os, unittest, re, io

try :
    import src
except ImportError :
    path = os.path.normpath(os.path.abspath( os.path.join( os.path.split(__file__)[0], "..", "..")))
    if path not in sys.path : sys.path.append (path)
    import src

from src.pyquickhelper.loghelper.flog           import fLOG
from src.pyquickhelper.loghelper.pyrepo_helper  import SourceRepository


class TestPySvnHelper (unittest.TestCase):

    def test_repo_version (self) :
        fLOG (__file__, self._testMethodName, OutputPrint = __name__ == "__main__")
        path = os.path.split(__file__)[0]
        data = os.path.abspath(os.path.join(path, "..", ".."))
        src = SourceRepository()
        all = src.version(data)
        fLOG("version",all)
        assert isinstance(all,int) or isinstance(all,str)


if __name__ == "__main__"  :
    unittest.main ()    
