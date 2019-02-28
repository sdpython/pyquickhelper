"""
@brief      test log(time=2s)
"""

import sys
import os
import unittest
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

from src.pyquickhelper.pycode import ExtTestCase
from src.pyquickhelper.pandashelper import df2html, df2rst


class TestPandasHelper_df2(ExtTestCase):

    def test_src_import(self):
        """for pylint"""
        self.assertTrue(src is not None)

    def test_df2(self):
        data = os.path.join(os.path.abspath(os.path.dirname(__file__)), "data")
        mara = os.path.join(data, "marathon.txt")
        df = pandas.read_csv(
            mara, names=["city", "year", "time", "seconds"], sep="\t")
        conv = df2html(df)
        self.assertStartsWith("<table>", conv)
        self.assertEndsWith("</table>\n", conv)


if __name__ == "__main__":
    unittest.main()
