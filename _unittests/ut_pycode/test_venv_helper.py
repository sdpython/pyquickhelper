"""
@brief      test tree node (time=50s)
"""

import sys
import os
import unittest

from pyquickhelper.loghelper import fLOG
from pyquickhelper.pycode import get_temp_folder, ExtTestCase
from pyquickhelper.pycode.venv_helper import create_virtual_env


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
