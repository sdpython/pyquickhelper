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

if __name__ == "__main__":
    unittest.main()
