"""
@brief      test log(time=1s)
"""
import os
import sys
import unittest
import datetime
import io
from tkinter import TclError

try:
    import src
except ImportError:
    path = os.path.normpath(
        os.path.abspath(
            os.path.join(
                os.path.split(__file__)[0],
                "..",
                "..")))
    if path not in sys.path:
        sys.path.append(path)
    import src

from src.pyquickhelper import fLOG
from src.pyquickhelper.funcwin.default_functions import _clean_name_variable, _get_format_zero_nb_integer, file_list


class TestMissingFuncWin (unittest.TestCase):

    def test_missing_funcwin(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        assert _clean_name_variable("s-6") == "s_6"
        assert _get_format_zero_nb_integer(5006) == "%04d"
        ioout = io.StringIO()
        file_list(os.path.abspath(os.path.dirname(__file__)), out=ioout)
        s = ioout.getvalue()
        assert len(s) > 0

if __name__ == "__main__":
    unittest.main()
