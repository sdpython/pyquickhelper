"""
@brief      test log(time=284s)
"""

import sys
import os
import unittest
import warnings


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

from src.pyquickhelper.loghelper import fLOG
from src.pyquickhelper.pycode._pylint_common import _private_test_style_src, _private_test_style_test


class TestSKIPpylint(unittest.TestCase):

    def test_src_import(self):
        """for pylint"""
        self.assertTrue(src is not None)

    def test_style_src(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        run_lint = True
        _private_test_style_src(fLOG, run_lint, verbose=True)

    def test_style_test(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        run_lint = True
        _private_test_style_test(fLOG, run_lint, verbose=True)


if __name__ == "__main__":
    unittest.main()
