"""
@brief      test tree node (time=2s)
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
from src.pyquickhelper.pycode import is_travis_or_appveyor
from src.pyquickhelper.serverdoc.ping_helper import regular_ping_machine


class TestPingHelper(unittest.TestCase):

    def test_src_import(self):
        """for pylint"""
        self.assertTrue(src is not None)

    def test_ping_list(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        if is_travis_or_appveyor():
            return
        regular_ping_machine('localhost', 0.5, nb_max=2, fLOG=fLOG)


if __name__ == "__main__":
    unittest.main()
