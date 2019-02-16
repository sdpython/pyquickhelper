"""
@brief      test log(time=10s)
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
from src.pyquickhelper import __file__ as PYQ
from src.pyquickhelper.pycode.call_setup_hook import call_setup_hook, call_setup_hook_cmd


class TestCallSetupHook(unittest.TestCase):

    def test_src_import(self):
        """for pylint"""
        self.assertTrue(src is not None)

    @unittest.skipIf(sys.platform == "darwin", reason="skipping on Mac OS")
    def test_call_setup_hook_cmd(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        cmd, code = call_setup_hook_cmd(
            "c:/__MOCK__", "pyquickhelper", interpreter_path="__PYTHON__")
        pyq = os.path.normpath(os.path.join(os.path.abspath(PYQ), "..", ".."))
        exp = '''__PYTHON__ -c "import sys;sys.path.append('c:/__MOCK__/src');sys.path.append('__PYQ__');''' + \
              '''from pyquickhelper import _setup_hook;_setup_hook();sys.exit(0)"'''
        exp = exp.replace("__PYQ__", pyq.replace("\\", "/"))
        cmd = cmd.replace("/home/travis/build/sdpython/pyquickhelper/", "")
        exp = exp.replace("/home/travis/build/sdpython/pyquickhelper/", "")
        cmd = cmd.replace("/home/circleci/repo/src/", "")
        exp = exp.replace("/home/circleci/repo/src/", "")
        cmd = cmd.replace("/home/circleci/repo/", "")
        exp = exp.replace("/home/circleci/repo/", "")
        cmd = cmd.replace("/root/github/pyquickhelper/", "")
        exp = exp.replace("/root/github/pyquickhelper/", "")
        cmd = cmd.replace("/home/vsts/work/1/s/", "")
        exp = exp.replace("/home/vsts/work/1/s/", "")
        for sub in ["/Users/vsts/agent/2.144.0/work/1/s/",
                    "/Users/vsts/agent/2.144.2/work/1/s/"]:
            cmd = cmd.replace(sub, "")
            exp = exp.replace(sub, "")
        rem = "/var/lib/jenkins/workspace/pyquickhelper/pyquickhelper_UT_%d%d_std/" % sys.version_info[:2]
        cmd = cmd.replace(rem, "")
        exp = exp.replace(rem, "")
        if exp != cmd:
            raise Exception("\nCMD: {0}\nEXP: {1}".format(cmd, exp))

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

        out, err = call_setup_hook(
            init, "pyquickhelper", fLOG=fLOG, use_print=False)
        fLOG(err)
        fLOG(out)
        self.assertEqual(err, "")

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
            unit_test=True, use_print=False)
        fLOG(err)
        fLOG(out)
        self.assertEqual(err, "")


if __name__ == "__main__":
    unittest.main()
