"""
@brief      test log(time=2s)
"""

import sys, os, unittest, re


try :
    import src
except ImportError :
    path = os.path.normpath(os.path.abspath( os.path.join( os.path.split(__file__)[0], "..", "..")))
    if path not in sys.path : sys.path.append (path)
    import src

from src.pyquickhelper import AutoCompletion, fLOG, AutoCompletionFile, open_html_form



class TestAutoCompletion (unittest.TestCase):

    def test_completion(self) :
        fLOG (__file__, self._testMethodName, OutputPrint = __name__ == "__main__")
        root = AutoCompletion()
        cl = root._add("name", "TestAutoCompletion")
        cl._add("method", "test_completion")
        cl._add("method2", "test_completion")
        cl = root._add("name2", "TestAutoCompletion2")
        cl._add("method3", "test_completion")
        s = str(root)
        fLOG("\n"+s)
        assert " |   |- method2" in s
        l = len(root)
        fLOG("l=",l)
        assert l == 6
        fLOG(root._)

    def test_completion_file(self):
        fLOG (__file__, self._testMethodName, OutputPrint = __name__ == "__main__")
        fold = os.path.abspath(os.path.split(__file__)[0])
        fold = os.path.join(fold, "..")
        this = AutoCompletionFile(fold)
        l = len(this)
        assert l > 30

    def test_html_form(self):
        fLOG (__file__, self._testMethodName, OutputPrint = __name__ == "__main__")
        params = {"parA":"valueA", "parB":"valueB"}
        title = 'unit_test_title'
        key_save = 'jjj'
        raw = open_html_form(params, title, key_save, raw=True)
        fLOG(raw)
        assert len(raw) > 0



if __name__ == "__main__"  :
    unittest.main ()