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
from src.pyquickhelper.pycode import is_travis_or_appveyor, skipif_travis
from src.pyquickhelper.pycode._pylint_common import _private_test_style_src, _private_test_style_test


class TestCodeStyle(unittest.TestCase):

    def test_src_import(self):
        """for pylint"""
        self.assertTrue(src is not None)

    @skipif_travis("source are cloned in a folder with /build/ inside")
    def test_style_src(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        if sys.version_info[0] == 2:
            warnings.warn(
                "skipping test_code_style because of Python 2 or " + sys.executable)
            return

        run_lint = is_travis_or_appveyor(env=['NAME_JENKINS']) is None
        _private_test_style_src(fLOG, run_lint, verbose='-v' in sys.argv)

    @skipif_travis("source are cloned in a folder with /build/ inside")
    def test_style_test(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        if sys.version_info[0] == 2:
            warnings.warn(
                "skipping test_code_style because of Python 2 or " + sys.executable)
            return

        run_lint = is_travis_or_appveyor(env=['NAME_JENKINS']) is None
        _private_test_style_test(fLOG, run_lint, verbose='-v' in sys.argv)


if __name__ == "__main__":
    unittest.main()
