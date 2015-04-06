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

from src.pyquickhelper import str_to_datetime, fLOG


class TestConvert(unittest.TestCase):

    def test_convert_date(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        assert str_to_datetime("2015-04-05").year == 2015
        assert str_to_datetime("2015-04-05T04:08:08").year == 2015


if __name__ == "__main__":
    unittest.main()
