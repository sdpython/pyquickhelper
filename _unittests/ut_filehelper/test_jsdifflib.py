"""
@brief      test tree node (time=7s)
"""
import sys
import os
import unittest
import warnings

import pyquickhelper.filehelper.visual_sync
from pyquickhelper.loghelper.flog import fLOG
from pyquickhelper.pycode import ExtTestCase
from pyquickhelper.filehelper.visual_sync import create_visual_diff_through_html


class TestJsDiffLib(ExtTestCase):

    def test_jsdifflib(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        tt = os.path.split(
            pyquickhelper.filehelper.visual_sync.__file__)[0]
        ma = tt
        p = create_visual_diff_through_html("a", "b")
        self.assertNotEmpty(p)
        self.assertExists(os.path.join(ma, "difflib.js"))


if __name__ == "__main__":
    unittest.main()
