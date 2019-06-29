"""
@brief      test log(time=2s)
"""

import os
import unittest
import pandas

from pyquickhelper.pycode import ExtTestCase
from pyquickhelper.pandashelper import df2rst


class TestPandasRst(ExtTestCase):

    def test_pandas_rst(self):
        df = pandas.DataFrame([{"A": "x", "AA": "xx", "AAA": "xxx"},
                               {"AA": "xxxxxxx", "AAA": "xxx"}])
        rst = df2rst(df)
        exp = """+---+---------+-----+
                 | A | AA      | AAA |
                 +===+=========+=====+
                 | x | xx      | xxx |
                 +---+---------+-----+
                 |   | xxxxxxx | xxx |
                 +---+---------+-----+
                 """.replace("                 ", "")
        self.assertEqual(rst, exp)

    def test_pandas_rst_right(self):
        df = pandas.DataFrame([{"A": "x", "AA": "xx", "AAA": "xxx"},
                               {"AA": "xxxxxxx", "AAA": "xxx"}])
        rst = df2rst(df, align="r")
        exp = """+---+---------+-----+
                 | A |      AA | AAA |
                 +===+=========+=====+
                 | x |      xx | xxx |
                 +---+---------+-----+
                 |   | xxxxxxx | xxx |
                 +---+---------+-----+
                 """.replace("                 ", "")
        self.assertEqual(rst, exp)

        rst = df2rst(df, align="c")
        exp = """+---+---------+-----+
                 | A |   AA    | AAA |
                 +===+=========+=====+
                 | x |   xx    | xxx |
                 +---+---------+-----+
                 |   | xxxxxxx | xxx |
                 +---+---------+-----+
                 """.replace("                 ", "")
        self.assertEqual(rst, exp)

    def test_pandas_rst_right_format_number(self):
        df = pandas.DataFrame([{"A": "x", "AA": "xx", "AAA": "xxx"},
                               {"AA": "xxxxxxx", "AAA": "xxx"}])
        rst = df2rst(df, align="r", number_format=4)
        exp = """+---+---------+-----+
                 | A |      AA | AAA |
                 +===+=========+=====+
                 | x |      xx | xxx |
                 +---+---------+-----+
                 |   | xxxxxxx | xxx |
                 +---+---------+-----+
                 """.replace("                 ", "")
        self.assertEqual(rst, exp)

        rst = df2rst(df, align="c", number_format=4)
        exp = """+---+---------+-----+
                 | A |   AA    | AAA |
                 +===+=========+=====+
                 | x |   xx    | xxx |
                 +---+---------+-----+
                 |   | xxxxxxx | xxx |
                 +---+---------+-----+
                 """.replace("                 ", "")
        self.assertEqual(rst, exp)

        df = pandas.DataFrame([{"A": "x", "AA": "xx", "AAA": "xxx", 'N': 0.5123456},
                               {"AA": "xxxxxxx", "AAA": "xxx"}])
        rst = df2rst(df, number_format=4)
        exp = """+---+---------+-----+--------+
                 | A | AA      | AAA | N      |
                 +===+=========+=====+========+
                 | x | xx      | xxx | 0.5123 |
                 +---+---------+-----+--------+
                 |   | xxxxxxx | xxx |        |
                 +---+---------+-----+--------+
                 """.replace("                 ", "")
        self.assertEqual(rst, exp)

    def test_pandas_rst_size(self):
        df = pandas.DataFrame([{"A": "x", "AA": "xx", "AAA": "xxx"},
                               {"AA": "xxxxxxx", "AAA": "xxx"}])
        rst = df2rst(df, column_size=[1, 1, 2])
        exp = """+---+---------+--------+
                 | A | AA      | AAA    |
                 +===+=========+========+
                 | x | xx      | xxx    |
                 +---+---------+--------+
                 |   | xxxxxxx | xxx    |
                 +---+---------+--------+
                 """.replace("                 ", "")
        self.assertEqual(rst, exp)

    def test_pandas_rst_size_table(self):
        df = pandas.DataFrame([{"A": "x", "AA": "xx", "AAA": "xxx"},
                               {"AA": "xxxxxxx", "AAA": "xxx"}])
        rst = df2rst(df, column_size=[1, 1, 2], list_table=True)
        exp = """
                    .. list-table::
                        :widths: 1 1 2
                        :header-rows: 1

                        * - A
                          - AA
                          - AAA
                        * - x
                          - xx
                          - xxx
                        * -
                          - xxxxxxx
                          - xxx
                    """.replace("                    ", "")
        self.assertEqual(rst.strip("\n "), exp.strip("\n "))

    def test_pandas_rst_size_table_title(self):
        df = pandas.DataFrame([{"A": "x", "AA": "xx", "AAA": "xxx"},
                               {"AA": "xxxxxxx", "AAA": "xxx"}])
        rst = df2rst(df, column_size=[1, 1, 2],
                     list_table=True, title="title__")
        exp = """
                    .. list-table:: title__
                        :widths: 1 1 2
                        :header-rows: 1

                        * - A
                          - AA
                          - AAA
                        * - x
                          - xx
                          - xxx
                        * -
                          - xxxxxxx
                          - xxx
                    """.replace("                    ", "")
        self.assertEqual(rst.strip("\n "), exp.strip("\n "))

    def test_pandas_rst_size_table_auto(self):
        df = pandas.DataFrame([{"A": "x", "AA": "xx", "AAA": "xxx"},
                               {"AA": "xxxxxxx", "AAA": "xxx"}])
        rst = df2rst(df, list_table=True)
        exp = """
                    .. list-table::
                        :widths: auto
                        :header-rows: 1

                        * - A
                          - AA
                          - AAA
                        * - x
                          - xx
                          - xxx
                        * -
                          - xxxxxxx
                          - xxx
                    """.replace("                    ", "")
        self.assertEqual(rst.strip("\n "), exp.strip("\n "))

    def test_pandas_rst_size_table_noheader(self):
        df = pandas.DataFrame([{"A": "x", "AA": "xx", "AAA": "xxx"},
                               {"AA": "xxxxxxx", "AAA": "xxx"}])
        rst = df2rst(df, list_table=True, header=False)
        exp = """
                    .. list-table::
                        :widths: auto

                        * - x
                          - xx
                          - xxx
                        * -
                          - xxxxxxx
                          - xxx
                    """.replace("                    ", "")
        self.assertEqual(rst.strip("\n "), exp.strip("\n "))

    def test_pandas_rst_size_table_number_format(self):
        df = pandas.DataFrame([{"A": 2.12345678, "AA": 3.12345678,
                                "AAA": 4.12345678},
                               {"AA": 2.12345678e10, "AAA": 2.12345678e-10}])
        rst = df2rst(df, list_table=True, header=False, number_format=3)
        exp = """
                    .. list-table::
                        :widths: auto

                        * - 2.12
                          - 3.12
                          - 4.12
                        * -
                          - 2.12e+10
                          - 2.12e-10
                    """.replace("                    ", "")
        self.assertEqual(rst.strip("\n "), exp.strip("\n "))


if __name__ == "__main__":
    unittest.main()
