"""
@brief      test tree node (time=5s)
"""
import sys
import os
import unittest
import warnings
import pandas

from pyquickhelper.pycode import ExtTestCase
from pyquickhelper.pandashelper import df2rst
from pyquickhelper import __file__ as rootfile
from pyquickhelper.pycode.profiling import profile


class TestProfiling(ExtTestCase):

    def test_profile(self):

        def simple():
            df = pandas.DataFrame([{"A": "x", "AA": "xx", "AAA": "xxx"},
                                   {"AA": "xxxxxxx", "AAA": "xxx"}])
            return df2rst(df)

        rootrem = os.path.normpath(os.path.abspath(
            os.path.join(os.path.dirname(rootfile), '..')))
        ps, res = profile(simple, rootrem=rootrem)
        res = res.replace('\\', '/')
        self.assertIn('pyquickhelper/pandashelper/tblformat.py', res)
        self.assertNotEmpty(ps)

    def test_profile_df(self):

        def simple():

            def simple2():
                df = pandas.DataFrame([{"A": "x", "AA": "xx", "AAA": "xxx"},
                                       {"AA": "xxxxxxx", "AAA": "xxx"}])
                return df2rst(df)
            return simple2()

        rootrem = os.path.normpath(os.path.abspath(
            os.path.join(os.path.dirname(rootfile), '..')))
        ps, df = profile(simple, rootrem=rootrem, as_df=True)
        self.assertIsInstance(df, pandas.DataFrame)
        self.assertEqual(df.loc[0, 'fct'], 'simple2')


if __name__ == "__main__":
    unittest.main()
