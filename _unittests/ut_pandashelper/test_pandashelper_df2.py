"""
@brief      test log(time=2s)
"""

import os
import unittest
import pandas

from pyquickhelper.pycode import ExtTestCase
from pyquickhelper.pandashelper import df2html, df2rst


class TestPandasHelper_df2(ExtTestCase):

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
