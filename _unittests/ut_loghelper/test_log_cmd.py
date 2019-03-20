"""
@brief      test log(time=1s)
"""
import sys
import os
import unittest

from pyquickhelper.loghelper.flog import fLOG
from pyquickhelper.loghelper.run_cmd import split_cmp_command, run_cmd, skip_run_cmd


class TestLogFunc (unittest.TestCase):

    def test_split_cmp_command(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        self.assertEqual(split_cmp_command("ab cd ef"), ["ab", "cd", "ef"])
        r = split_cmp_command('ab "cd ef"')
        if r != ["ab", 'cd ef']:
            raise Exception(r)
        self.assertEqual(split_cmp_command('"ab cd" ef'), ["ab cd", "ef"])
        self.assertEqual(split_cmp_command('"ab" cd ef'), ["ab", "cd", "ef"])
        self.assertEqual(split_cmp_command('"ab cd ef"'), ["ab cd ef"])

    def test_run_cmd_simple(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        if sys.platform.startswith("win"):
            cmd = "dir ."
        else:
            cmd = "ls ."
        out1, err = run_cmd(cmd, wait=True, fLOG=fLOG)
        out2, err = run_cmd(cmd, wait=True, communicate=False, fLOG=fLOG)

        fLOG("***", out1)
        fLOG("***", out2)

        out3, err = run_cmd(
            cmd, wait=True, communicate=True, fLOG=fLOG)
        fLOG("***", out3)

        out, err = skip_run_cmd(cmd, wait=True)
        assert len(out) == 0
        assert len(err) == 0


if __name__ == "__main__":
    unittest.main()
