"""
@brief      test tree node (time=5s)
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
from src.pyquickhelper.pycode import clean_files, ExtTestCase


class TestCleanFile(ExtTestCase):

    def test_clean_file(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        folder = os.path.abspath(os.path.dirname(__file__))
        res = clean_files(folder, fLOG=fLOG, posreg="test_clean.*[.]py$")
        self.assertEmpty(res)


if __name__ == "__main__":
    unittest.main()
