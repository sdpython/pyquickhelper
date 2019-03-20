"""
@brief      test log(time=0s)
"""

import sys
import os
import unittest

if "temp_" in os.path.abspath(__file__):
    raise ImportError(
        "this file should not be imported in that location: " +
        os.path.abspath(__file__))

from pyquickhelper.loghelper import fLOG, str2datetime


class TestConvert(unittest.TestCase):

    def test_convert_date(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        assert str2datetime("2015-04-05").year == 2015
        assert str2datetime("2015-04-05T04:08:08").year == 2015


if __name__ == "__main__":
    unittest.main()
