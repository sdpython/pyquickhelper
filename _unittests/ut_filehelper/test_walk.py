"""
@brief      test log(time=2s)
@author     Xavier Dupre
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

        if sys.version_info[0] >= 3:
            nb2 = 0
            for root, dirs, files in walk(ut, neg_filter="*ut_loghelper*"):
                nb2 += 1

            self.assertGreater(nb2, 0)
            self.assertLesser(nb2, nb)
        else:
            nb2 = 1e6

        def filter(d):
            return "loghelper" in d or "helpgen" in d

        nb3 = 0
        for root, dirs, files in walk(ut, neg_filter=filter):
            nb3 += 1

        self.assertGreater(nb3, 0)
        self.assertLesser(nb3, nb2)


if __name__ == "__main__":
    unittest.main()
