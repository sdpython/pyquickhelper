"""
@brief      test log(time=5s)
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
from src.pyquickhelper.pycode.call_setup_hook import call_setup_hook


class TestCallSetupHook(unittest.TestCase):

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
        assert err == "no ______"

        out, err = call_setup_hook(init, "pyquickhelper", fLOG=fLOG)
        fLOG(err)
        fLOG(out)
        assert len(err) == 0

if __name__ == "__main__":
    unittest.main()
