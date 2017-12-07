"""
@brief      test log(time=1s)
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

from src.pyquickhelper.loghelper.flog import fLOG
from src.pyquickhelper.loghelper import run_cmd, reap_children


class TestProcessHelper(unittest.TestCase):

    def test_reap_children(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        cmd = "pause"
        proc, _ = run_cmd(cmd, wait=False, fLOG=fLOG)
        self.assertTrue(_ is None)
        ki = reap_children(fLOG=fLOG)
        self.assertEqual(len(ki), 1)
        # fLOG(ki)
        # To avoid a warning.
        proc.returncode = 0


if __name__ == "__main__":
    unittest.main()
