"""
@brief      test tree node (time=50s)
"""

import sys
import os
import unittest
import re
import shutil
import warnings
import pandas

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

from src.pyquickhelper import fLOG, get_temp_folder
from src.pyquickhelper.pycode.venv_helper import create_virtual_env


class TestVenvHelper(unittest.TestCase):

    def test_venv_empty(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        if __name__ != "__main__":
            # does not accept virtual environment
            return

        temp = get_temp_folder(__file__, "temp_venv_empty")
        out = create_virtual_env(temp, fLOG=fLOG)
        fLOG("-----")
        fLOG(out)
        fLOG("-----")
        pyt = os.path.join(temp, "Scripts")
        assert os.path.exists(pyt)
        lo = os.listdir(pyt)
        assert len(lo) > 0


if __name__ == "__main__":
    unittest.main()
