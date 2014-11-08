"""
@brief      test log(time=3s)
"""
import os, sys, unittest, tkinter

try :
    import src
except ImportError :
    path = os.path.normpath(os.path.abspath( os.path.join( os.path.split(__file__)[0], "..", "..")))
    if path not in sys.path : sys.path.append (path)
    import src

from src.pyquickhelper.loghelper.flog import fLOG
from src.pyquickhelper.funcwin.storing_functions import get_icon
from src.pyquickhelper.funcwin.frame_function import open_window_function

from src.pyquickhelper.funcwin.default_functions import test_regular_expression

class TestMakeWindow (unittest.TestCase):

    def test_FrameFunction (self) :
        fLOG (__file__, self._testMethodName, OutputPrint = __name__ == "__main__")

        ico = get_icon()
        fLOG("icon",ico)
        assert os.path.exists(ico)

        if __name__ == "__main__" :
            open_window_function(test_regular_expression)

    def test_open_window_params(self):
        fLOG (__file__, self._testMethodName, OutputPrint = __name__ == "__main__")
        if __name__ == "__main__" :
            par = { "user":os.environ["USERNAME"],
                    "password":"" }
            res = open_window_params(par,
                          help_string = "unit test",
                          title = "try the password *",
                          top_level_window = None,
                          key_save = "unique")
            fLOG(res)


if __name__ == "__main__"  :
    unittest.main ()