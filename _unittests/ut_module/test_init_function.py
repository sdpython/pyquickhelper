"""
@brief      test log(time=8s)
@author     Xavier Dupre
"""
import io
import sys
import os
import unittest
from contextlib import redirect_stdout

from pyquickhelper.loghelper import fLOG
from pyquickhelper import check, _setup_hook, get_insetup_functions


class TestInitFunction(unittest.TestCase):

    def test_check(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        check()

    def test_hook(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        _setup_hook()
        buf = io.StringIO()
        with redirect_stdout(buf):
            _setup_hook(True)
        self.assertIn('Success', buf.getvalue())

    def test_insetup(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        get_insetup_functions()


if __name__ == "__main__":
    unittest.main()
