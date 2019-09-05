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

    def test_df2rst_split_row(self):
        data = os.path.join(os.path.abspath(os.path.dirname(__file__)), "data")
        mara = os.path.join(data, "marathon.txt")
        df = pandas.read_csv(
            mara, names=["city", "year", "time", "seconds"], sep="\t")
        conv = df2rst(df, split_row="city")
        self.assertIn("+++++++++", conv)
        self.assertIn("| city      | year | time     | seconds |", conv)
        self.assertIn("| PARIS | 2011 | 02:06:29 | 7589    |", conv)

        conv = df2rst(df, split_row="year")
        self.assertIn("++++", conv)
        self.assertIn("| city      | year | time     | seconds |", conv)
        self.assertIn("| FUKUOKA   | 1976 | 02:12:35 | 7955    |", conv)

        conv = df2rst(df, split_row=["city", "year"])
        self.assertIn("'AMSTERDAM', 1975", conv)
        self.assertIn("| city      | year | time     | seconds |", conv)

    def test_df2rst_split_col(self):
        data = os.path.join(os.path.abspath(os.path.dirname(__file__)), "data")
        mara = os.path.join(data, "marathon.txt")
        df = pandas.read_csv(
            mara, names=["city", "year", "time", "seconds"], sep="\t")
        self.assertRaise(lambda: df2rst(df, split_col_common=["city", "time"],
                                        split_col_subsets=[['time'], ['seconds']]),
                         ValueError)
        conv = df2rst(df, split_col_common=["city", "year"],
                      split_col_subsets=[['time'], ['seconds']])
        self.assertIn("| CHICAGO   | 2005 | 7622    |", conv)

    def test_df2rst_split_col_row(self):
        data = os.path.join(os.path.abspath(os.path.dirname(__file__)), "data")
        mara = os.path.join(data, "marathon.txt")
        df = pandas.read_csv(
            mara, names=["city", "year", "time", "seconds"], sep="\t")
        conv = df2rst(df, split_row="city",
                      split_col_common=["city", "year"],
                      split_col_subsets=[['time'], ['seconds']])
        self.assertIn("+++++++++", conv)
        self.assertIn("| STOCKOLM | 2007 | 8456    |", conv)


if __name__ == "__main__":
    unittest.main()
