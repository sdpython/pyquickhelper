"""
@brief      test log(time=3s)
"""


import sys
import os
import unittest

from pyquickhelper.loghelper.flog import fLOG
from pyquickhelper.loghelper.run_cmd import run_cmd


class TestRunCmdTimeout(unittest.TestCase):

    def test_run_cmd_timeout(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        if __name__ == "__main__":
            cmd = "more"
            out, err = run_cmd(cmd, wait=True, fLOG=fLOG,
                               tell_if_no_output=1, communicate=False, timeout=3)
            fLOG(out)
            fLOG(err)
            assert "Process killed" in err
            # kill does not work


if __name__ == "__main__":
    unittest.main()
