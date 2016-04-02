"""
@brief      test log(time=8s)
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

from src.pyquickhelper.loghelper.flog import fLOG, run_cmd
from src.pyquickhelper.helpgen.process_notebooks import get_ipython_program, get_jupyter_convert_program
from src.pyquickhelper.pycode.ci_helper import is_travis_or_appveyor


class TestGetProgram(unittest.TestCase):

    def test_get_ipython(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        if is_travis_or_appveyor() == "travis":
            return
        exe = get_ipython_program()
        cmd = exe + " help"
        out, err = run_cmd(cmd, wait=True)
        # fLOG(out)
        assert "DEPRECATED" in out

    def test_get_jupyter_convert(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        if is_travis_or_appveyor():
            return
        exe = get_jupyter_convert_program()
        cmd = exe + " --help"
        out, err = run_cmd(cmd, wait=True)
        fLOG(out)
        assert "--output=" in out

if __name__ == "__main__":
    unittest.main()
