"""
@brief      test tree node (time=50s)
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
from src.pyquickhelper.pycode import get_temp_folder, ExtTestCase
from src.pyquickhelper.pycode.venv_helper import create_virtual_env


class TestVenvHelper(ExtTestCase):

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
        self.assertExists(pyt)
        lo = os.listdir(pyt)
        self.assertNotEmpty(lo)


if __name__ == "__main__":
    unittest.main()
