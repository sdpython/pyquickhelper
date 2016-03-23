"""
@brief      test log(time=2s)
@author     Xavier Dupre
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

from src.pyquickhelper import fLOG, get_temp_folder
from src.pyquickhelper.filehelper import walk


class TestWalk(unittest.TestCase):

    def test_walk(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        this = os.path.abspath(os.path.dirname(__file__))
        ut = os.path.join(this, "..")
        fLOG(this)
        nb = 0
        for root, dirs, files in walk(ut):
            nb += 1

        nb2 = 0
        for root, dirs, files in walk(ut, neg_filter="*ut_loghelper*"):
            nb2 += 1

        assert nb2 > 0
        assert nb2 < nb

        def filter(d):
            return "loghelper" in d or "helpgen" in d

        nb3 = 0
        for root, dirs, files in walk(ut, neg_filter=filter):
            nb3 += 1

        assert nb3 > 0
        assert nb3 < nb2

if __name__ == "__main__":
    unittest.main()
