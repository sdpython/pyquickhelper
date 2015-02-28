"""
@brief      test log(time=1s)
"""
import os, sys, unittest, datetime

try :
    import src
except ImportError :
    path = os.path.normpath(os.path.abspath( os.path.join( os.path.split(__file__)[0], "..", "..")))
    if path not in sys.path : sys.path.append (path)
    import src

from src.pyquickhelper.loghelper.flog import fLOG
from src.pyquickhelper import check, open_window_params, open_window_function
from src.pyquickhelper.funcwin.function_helper import get_function_list, has_unknown_parameters,  private_get_function

def test_function(a,b):
    """
    return a+b
    @param      a   (float) float
    @param      b   (float) float
    @return         a+b
    """
    return a+b

class TestWindows (unittest.TestCase):

    def test_open_window_params(self) :
        fLOG(__file__, self._testMethodName, OutputPrint = __name__ == "__main__")
        params = dict(p1="p1", p2=3)
        win = open_window_params(params, do_not_open=True)
        fLOG(type(win))
        assert isinstance(win, src.pyquickhelper.funcwin.frame_params.FrameParams)

    def test_open_window_function(self) :
        fLOG(__file__, self._testMethodName, OutputPrint = __name__ == "__main__")
        func = test_function
        win = open_window_function(func, do_not_open=True)
        fLOG(type(win))
        assert isinstance(win, src.pyquickhelper.funcwin.frame_function.FrameFunction)

    def test_get_function_list(self):
        fLOG(__file__, self._testMethodName, OutputPrint = __name__ == "__main__")
        funcs = get_function_list(src.pyquickhelper)
        assert isinstance(funcs, dict)
        assert len(funcs) > 0
        assert "df2rst" in funcs
        r = has_unknown_parameters(funcs["df2rst"])
        assert not r
        f =  private_get_function("os.listdir")
        fLOG("**",f)



if __name__ == "__main__"  :
    unittest.main ()