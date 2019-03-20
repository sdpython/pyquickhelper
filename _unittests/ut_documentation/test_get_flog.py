# -*- coding: utf-8 -*-
"""
@brief      test log(time=2s)
"""

import sys
import os
import unittest

from pyquickhelper.loghelper import fLOG
from pyquickhelper import get_fLOG


class TestGetfLOG(unittest.TestCase):

    def test_flog(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        f1 = get_fLOG(True)
        self.assertTrue(f1 is not None)
        f2 = get_fLOG(False)
        self.assertTrue(f2 is not None)
        self.assertTrue(f1 != f2)


if __name__ == "__main__":
    unittest.main()
