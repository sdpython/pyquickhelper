"""
@brief      test log(time=2s)
"""

import os
import unittest
import pandas

from pyquickhelper.pycode import ExtTestCase
from pyquickhelper.pandashelper import df2html, df2rst


class TestPandasHelper_df2(ExtTestCase):

    def test_df2html(self):
        data = os.path.join(os.path.abspath(os.path.dirname(__file__)), "data")
        mara = os.path.join(data, "marathon.txt")
        df = pandas.read_csv(
            mara, names=["city", "year", "time", "seconds"], sep="\t")
        conv = df2html(df)
        self.assertStartsWith("<table>", conv)
        self.assertEndsWith("</table>\n", conv)

    def test_df2rst(self):
        data = os.path.join(os.path.abspath(os.path.dirname(__file__)), "data")
        mara = os.path.join(data, "marathon.txt")
        df = pandas.read_csv(
            mara, names=["city", "year", "time", "seconds"], sep="\t")
        conv = df2rst(df)
        self.assertIn("| city      | year | time     | seconds |", conv)
        self.assertIn("| PARIS     | 2011 | 02:06:29 | 7589    |", conv)

    def test_df2rst_split(self):
        data = os.path.join(os.path.abspath(os.path.dirname(__file__)), "data")
        mara = os.path.join(data, "marathon.txt")
        df = pandas.read_csv(
            mara, names=["city", "year", "time", "seconds"], sep="\t")
        conv = df2rst(df, split="city")
        self.assertIn("+++++++++", conv)
        self.assertIn("| city      | year | time     | seconds |", conv)
        self.assertIn("| PARIS | 2011 | 02:06:29 | 7589    |", conv)

        conv = df2rst(df, split="year")
        self.assertIn("++++", conv)
        self.assertIn("| city      | year | time     | seconds |", conv)
        self.assertIn("| FUKUOKA   | 1976 | 02:12:35 | 7955    |", conv)

        conv = df2rst(df, split=["city", "year"])
        self.assertIn("'AMSTERDAM', 1975", conv)
        self.assertIn("| city      | year | time     | seconds |", conv)


if __name__ == "__main__":
    unittest.main()
