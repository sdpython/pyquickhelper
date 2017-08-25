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

from src.pyquickhelper.loghelper import fLOG
from src.pyquickhelper.pandashelper import df2rst


class TestPandasRst(unittest.TestCase):

    def test_pandas_rst(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        df = pandas.DataFrame([{"A": "x", "AA": "xx", "AAA": "xxx"},
                               {"AA": "xxxxxxx", "AAA": "xxx"}])
        rst = df2rst(df)
        exp = """+-----+---------+-----+
                 | A   | AA      | AAA |
                 +=====+=========+=====+
                 | x   | xx      | xxx |
                 +-----+---------+-----+
                 |     | xxxxxxx | xxx |
                 +-----+---------+-----+
                 """.replace("                 ", "")
        self.assertEqual(rst, exp)

    def test_pandas_rst_right(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        df = pandas.DataFrame([{"A": "x", "AA": "xx", "AAA": "xxx"},
                               {"AA": "xxxxxxx", "AAA": "xxx"}])
        rst = df2rst(df, align="r")
        exp = """+-----+---------+-----+
                 |   A |      AA | AAA |
                 +=====+=========+=====+
                 |   x |      xx | xxx |
                 +-----+---------+-----+
                 |     | xxxxxxx | xxx |
                 +-----+---------+-----+
                 """.replace("                 ", "")
        self.assertEqual(rst, exp)

        rst = df2rst(df, align="c")
        exp = """+-----+---------+-----+
                 |  A  |   AA    | AAA |
                 +=====+=========+=====+
                 |  x  |   xx    | xxx |
                 +-----+---------+-----+
                 |     | xxxxxxx | xxx |
                 +-----+---------+-----+
                 """.replace("                 ", "")
        self.assertEqual(rst, exp)

    def test_pandas_rst_size(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        df = pandas.DataFrame([{"A": "x", "AA": "xx", "AAA": "xxx"},
                               {"AA": "xxxxxxx", "AAA": "xxx"}])
        rst = df2rst(df, column_size=[1, 1, 2])
        exp = """+-----+---------+--------+
                 | A   | AA      | AAA    |
                 +=====+=========+========+
                 | x   | xx      | xxx    |
                 +-----+---------+--------+
                 |     | xxxxxxx | xxx    |
                 +-----+---------+--------+
                 """.replace("                 ", "")
        self.assertEqual(rst, exp)

    def test_pandas_rst_size_table(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

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
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

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
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

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
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

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


if __name__ == "__main__":
    unittest.main()
