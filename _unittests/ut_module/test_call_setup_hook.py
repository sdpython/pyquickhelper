"""
@brief      test log(time=10s)
"""

import sys
import os
import unittest
import re


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

from src.pyquickhelper import fLOG
from src.pyquickhelper.pycode.call_setup_hook import call_setup_hook, call_setup_hook_cmd


class TestCallSetupHook(unittest.TestCase):

    def test_call_setup_hook_cmd(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        cmd, code = call_setup_hook_cmd(
            "c:/__MOCK__", "pyquickhelper", interpreter_path="__PYTHON__")
        exp = '''__PYTHON__ -c "import sys;sys.path.append('c:/__MOCK__/src');from pyquickhelper import _setup_hook;_setup_hook();sys.exit(0)"'''
        assert exp == cmd

    def test_call_setup_hook(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        init = os.path.join(
            os.path.split(__file__)[0],
            "..",
            "..")
        out, err = call_setup_hook(
            init, "pyquickhelper", fLOG=fLOG, function_name="______")
        fLOG(err)
        fLOG(out)
        if not(err == "no ______" or "linux" in out):
            raise Exception("OUT:\n{0}\nERR:\n{1}".format(out, err))

        out, err = call_setup_hook(init, "pyquickhelper", fLOG=fLOG)
        fLOG(err)
        fLOG(out)
        assert len(err) == 0

    def test_call_setup_hook_call(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        init = os.path.join(
            os.path.split(__file__)[0],
            "..",
            "..")
        out, err = call_setup_hook(
            init, "pyquickhelper", fLOG=fLOG, function_name="______", force_call=True)
        fLOG(err)
        fLOG(out)
        if not(err == "no ______" or "linux" in out):
            raise Exception("OUT:\n{0}\nERR:\n{1}".format(out, err))

        out, err = call_setup_hook(
            init, "pyquickhelper", fLOG=fLOG, force_call=True,
            additional_paths=["not a path"],
            unit_test=True)
        fLOG(err)
        fLOG(out)
        assert len(err) == 0

if __name__ == "__main__":
    unittest.main()
