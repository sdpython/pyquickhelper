"""
@brief      test tree node (time=5s)
"""


import sys
import os
import unittest

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
from src.pyquickhelper.texthelper import compare_module_version
from src.pyquickhelper.texthelper.version_helper import numeric_module_version


class TestVersionning(unittest.TestCase):

    def test_numpy_version(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        n1 = numeric_module_version('1.7.19')
        self.assertEqual(n1, (1, 7, 19))

    def test_compare_module_version(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        self.assertEqual(compare_module_version('1.7.19', '1.7.20'), -1)
        self.assertEqual(compare_module_version('1.7.19', '1.7.19'), 0)
        self.assertEqual(compare_module_version('1.7.19.20', '1.7.19'), 1)


if __name__ == "__main__":
    unittest.main()
