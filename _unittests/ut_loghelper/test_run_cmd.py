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

from src.pyquickhelper.pycode import get_temp_folder
from src.pyquickhelper.loghelper.flog import fLOG
from src.pyquickhelper.loghelper.run_cmd import run_cmd, skip_run_cmd


class TestRunCmd(unittest.TestCase):

    def test_run_cmd_1(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        temp = get_temp_folder(__file__, "temp_run_cmd_1")

        cmd = "dir ."
        fLOG("##########")
        out1, err = run_cmd(cmd, wait=True, fLOG=fLOG)
        fLOG("##########")
        out2, err = run_cmd(cmd, wait=True, communicate=False, fLOG=fLOG)
        fLOG("##########")

        fLOG("***", out1)
        fLOG("***", out2)

        secure = os.path.join(temp, "out_log_secure.txt")

        out3, err = run_cmd(
            cmd, wait=True, communicate=True, secure=secure, fLOG=fLOG)
        fLOG("***", out3)

        out, err = skip_run_cmd(cmd, wait=True)
        assert len(out) == 0
        assert len(err) == 0
        self.maxDiff = None
        self.assertEqual(out1.strip(), out2.strip())


if __name__ == "__main__":
    unittest.main()
