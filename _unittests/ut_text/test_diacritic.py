# -*- coding: utf-8 -*-
"""
@brief      test tree node (time=1s)
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
from src.pyquickhelper.texthelper import remove_diacritics


class TestDiacritic (unittest.TestCase):

    def test_src_import(self):
        """for pylint"""
        self.assertTrue(src is not None)

    def test_accent(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        self.assertEqual(remove_diacritics("enguérand"), "enguerand")


if __name__ == "__main__":
    unittest.main()
