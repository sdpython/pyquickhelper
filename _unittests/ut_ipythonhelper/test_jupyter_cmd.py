"""
@brief      test log(time=2s)

notebook test
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
from src.pyquickhelper.ipythonhelper import jupyter_cmd


class TestJupyterCmd(unittest.TestCase):

    def test_jupyter_cmd(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        out = jupyter_cmd()
        fLOG(out)
        assert "--runtime-dir" in out

if __name__ == "__main__":
    unittest.main()
