"""
@brief      test log(time=2s)
"""

import sys
import os
import unittest
import re
import numpy
import pandas


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

from src.pyquickhelper import read_url, fLOG, isempty, isnan
from src.pyquickhelper.pandashelper import df2html


class TestPandasHelper_df2(unittest.TestCase):

    def test_df2(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        data = os.path.join(os.path.abspath(os.path.dirname(__file__)), "data")
        mara = os.path.join(data, "marathon.txt")
        df = pandas.read_csv(
            mara, names=["city", "year", "time", "seconds"], sep="\t")
        conv = df2html(df)
        assert conv.startswith("<table>")
        assert conv.endswith("</table>\n")

if __name__ == "__main__":
    unittest.main()
