"""
@brief      test tree node (time=50s)
"""

import sys
import os
import unittest

from pyquickhelper.loghelper import fLOG
from pyquickhelper.pycode import skipif_travis, skipif_azure
from pyquickhelper.pycode.venv_helper import run_base_script, is_virtual_environment


class TestVenvBase(unittest.TestCase):

    @skipif_travis("no end on travis")
    @skipif_azure("does not work on azure")
    def test_run_base_script(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        this = os.path.abspath(__file__)
        this = os.path.join(os.path.dirname(
            this), "example_venv_base_simple.py")
        if is_virtual_environment():
            fLOG("virtual_environment")
            out = run_base_script(this, file=True, fLOG=fLOG)
        else:
            fLOG("no virtual_environment")
            out = run_base_script(this, file=True, fLOG=fLOG)
        if "example_venv_base_simple.py execution" not in out:
            raise Exception(out)


if __name__ == "__main__":
    unittest.main()
