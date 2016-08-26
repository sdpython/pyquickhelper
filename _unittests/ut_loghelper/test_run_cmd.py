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
from src.pyquickhelper.loghelper.run_cmd import run_cmd, skip_run_cmd


class TestRunCmd(unittest.TestCase):

    def test_run_cmd_1(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        cmd = "set"
        fLOG("##########")
        out1, err = run_cmd(cmd, wait=True, fLOG=fLOG)
        fLOG("##########")
        out2, err = run_cmd(cmd, wait=True, communicate=False, fLOG=fLOG)
        fLOG("##########")
        self.maxDiff = None
        self.assertEqual(out1.strip(), out2.strip())

    def test_run_cmd_2(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        cmd = "set"

        out3, err = run_cmd(
            cmd, wait=True, communicate=False, tell_if_no_output=600, fLOG=fLOG)
        fLOG("***", out3)

        out, err = skip_run_cmd(cmd, wait=True)
        assert len(out) == 0
        assert len(err) == 0
        counts = dict(out=[], err=[])

        def stop_running_if(out, err, counts=counts):
            if out:
                counts["out"].append(out)
            if err:
                counts["err"].append(err)

        out4, err = run_cmd(
            cmd, wait=True, communicate=False, tell_if_no_output=600,
            stop_running_if=stop_running_if, fLOG=fLOG)
        fLOG("***", out3)

        out, err = skip_run_cmd(cmd, wait=True)
        assert len(out) == 0
        assert len(err) == 0
        self.maxDiff = None
        self.assertEqual(out3.strip(), out4.strip())
        assert len(counts["out"]) > 0
        if len(counts["err"]) > 0:
            raise Exception(counts["err"])

    def test_run_cmd_more(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        cmd = "more " + os.path.abspath(__file__)

        try:
            run_cmd(cmd, wait=True, communicate=False,
                    tell_if_no_output=600, fLOG=fLOG, sin="\n\n\n" * 100)
        except:
            pass

        out, err = run_cmd(cmd, wait=True, communicate=True,
                           fLOG=fLOG, sin="\n\n\n" * 100)
        assert len(out) > 10
        assert len(err) == 0


if __name__ == "__main__":
    unittest.main()
