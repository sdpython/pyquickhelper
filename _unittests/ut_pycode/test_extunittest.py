"""
@brief      test tree node (time=5s)
"""


import sys
import os
import unittest
import warnings

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
from src.pyquickhelper.pycode import ExtTestCase

if sys.version_info[0] == 2:
    FileNotFoundError = Exception


class TestExtTestCase(ExtTestCase):

    def test_files(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        self.assertExists(__file__)
        self.assertRaise(lambda: self.assertExists(
            __file__ + ".k"), FileNotFoundError)

    def test_greater(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        self.assertGreater("c", "b")
        self.assertRaise(lambda: self.assertGreater("a", "b"), AssertionError)

    def test_lesser(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        self.assertLesser("a", "b")
        self.assertRaise(lambda: self.assertLesser("c", "b"), AssertionError)

    def test_df(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=ImportWarning)
            from pandas import DataFrame
        df = DataFrame(data=dict(a=["a"]))
        df1 = DataFrame(data=dict(a=["a"]))
        df2 = DataFrame(data=dict(a=["b"]))
        self.assertEqualDataFrame(df, df1)
        self.assertRaise(lambda: self.assertEqualDataFrame(
            df, df2), AssertionError)
        self.assertEqual(df, df1)
        self.assertRaise(lambda: self.assertEqual(
            df, df2), AssertionError)

    def test_arr(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        from numpy import array
        df = array([[0, 1], [1, 2]])
        df1 = array([[0, 1], [1, 2]])
        df2 = array([[0, 1], [3, 2]])
        self.assertEqualArray(df, df1)
        self.assertRaise(lambda: self.assertEqualArray(
            df, df2), AssertionError)

    def test_str(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        self.assertStartsWith("a", "ab")
        self.assertRaise(lambda: self.assertStartsWith(
            "ab", "a"), AssertionError)
        self.assertEndsWith("a", "ba")
        self.assertRaise(lambda: self.assertEndsWith(
            "ba", "a"), AssertionError)

    def test_not_empty(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        self.assertNotEmpty([0])
        self.assertRaise(lambda: self.assertNotEmpty(None), AssertionError)
        self.assertRaise(lambda: self.assertNotEmpty([]), AssertionError)


if __name__ == "__main__":
    unittest.main()
