# -*- coding: utf-8 -*-
"""
@brief      test tree node (time=1s)
"""


import sys
import os
import unittest

from pyquickhelper.loghelper import fLOG
from pyquickhelper.texthelper import remove_diacritics


class TestDiacritic (unittest.TestCase):

    def test_accent(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        self.assertEqual(remove_diacritics("enguérand"), "enguerand")


if __name__ == "__main__":
    unittest.main()
