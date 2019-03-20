"""
@brief      test log(time=1s)
"""


import sys
import os
import unittest

from pyquickhelper.loghelper import fLOG, fLOGFormat


class TestLogFuncFormat (unittest.TestCase):

    def test_log_format(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        res = fLOGFormat("\n", [4, 5], {3: 4})
        assert res.endswith(" [4, 5] {3: 4}\n")


if __name__ == "__main__":
    unittest.main()
