"""
@brief      test tree node (time=5s)
"""
import sys
import os
import unittest
import warnings
import time
from pstats import SortKey
import pandas
from pyquickhelper.pycode import ExtTestCase
from pyquickhelper.pandashelper import df2rst
from pyquickhelper import __file__ as rootfile
from pyquickhelper.pycode.profiling import (
    profile, profile2df, profile2graph, ProfileNode)


class TestProfiling(ExtTestCase):

    def test_profile(self):

        def simple():
            df = pandas.DataFrame([{"A": "x", "AA": "xx", "AAA": "xxx"},
                                   {"AA": "xxxxxxx", "AAA": "xxx"}])
            return df2rst(df)

        rootrem = os.path.normpath(os.path.abspath(
            os.path.join(os.path.dirname(rootfile), '..')))
        ps, res = profile(simple, rootrem=rootrem)  # pylint: disable=W0632
        res = res.replace('\\', '/')
        self.assertIn('pyquickhelper/pandashelper/tblformat.py', res)
        self.assertNotEmpty(ps)

        ps, res = profile(simple)  # pylint: disable=W0632
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
        ps, df = profile(simple, rootrem=rootrem,
                         as_df=True)  # pylint: disable=W0632
        self.assertIsInstance(df, pandas.DataFrame)
        self.assertEqual(df.loc[0, 'namefct'].split('-')[-1], 'simple')
        self.assertNotEmpty(ps)
        df = profile2df(ps, False)
        self.assertIsInstance(df, list)
        self.assertIsInstance(df[0], dict)
        df = profile2df(ps, True)
        self.assertIsInstance(df, pandas.DataFrame)

    def test_profile_df_verbose(self):
        calls = [0]

        def f0(t):
            calls[0] += 1
            time.sleep(t)

        def f1(t):
            calls[0] += 1
            time.sleep(t)

        def f2():
            calls[0] += 1
            f1(0.1)
            f1(0.01)

        def f3():
            calls[0] += 1
            f0(0.2)
            f1(0.5)

        def f4():
            calls[0] += 1
            f2()
            f3()

        ps = profile(f4)[0]  # pylint: disable=W0632
        df = self.capture(
            lambda: profile2df(ps, verbose=True, fLOG=print))[0]
        dfi = df.set_index('fct')
        self.assertEqual(dfi.loc['f4', 'ncalls1'], 1)
        self.assertEqual(dfi.loc['f4', 'ncalls2'], 1)

    def test_profile_pyinst(self):
        def simple():
            df = pandas.DataFrame([{"A": "x", "AA": "xx", "AAA": "xxx"},
                                   {"AA": "xxxxxxx", "AAA": "xxx"}])
            for i in range(0, 99):
                df2rst(df)
            return df2rst(df)

        ps, res = profile(
            simple, pyinst_format='text')  # pylint: disable=W0632
        self.assertIn('.py', res)
        self.assertNotEmpty(ps)
        ps, res = profile(
            simple, pyinst_format='textu')  # pylint: disable=W0632
        self.assertIn('Recorded', res)
        self.assertNotEmpty(ps)
        ps, res = profile(
            simple, pyinst_format='html')  # pylint: disable=W0632
        self.assertIn("</script>", res)
        self.assertNotEmpty(ps)
        self.assertRaise(lambda: profile(
            simple, pyinst_format='htmlgg'), ValueError)
        ps, res = profile(
            simple, pyinst_format='json')  # pylint: disable=W0632
        self.assertIn('"start_time"', res)
        self.assertNotEmpty(ps)

    def test_profile_graph(self):
        calls = [0]

        def f0(t):
            calls[0] += 1
            time.sleep(t)

        def f1(t):
            calls[0] += 1
            time.sleep(t)

        def f2():
            calls[0] += 1
            f1(0.1)
            f1(0.01)

        def f3():
            calls[0] += 1
            f0(0.2)
            f1(0.5)

        def f4():
            calls[0] += 1
            f2()
            f3()

        ps = profile(f4)[0]  # pylint: disable=W0632
        profile2df(ps, verbose=False, clean_text=lambda x: x.split('/')[-1])
        root, nodes = profile2graph(ps, clean_text=lambda x: x.split('/')[-1])
        self.assertEqual(len(nodes), 6)
        self.assertIsInstance(nodes, dict)
        self.assertIsInstance(root, ProfileNode)
        self.assertIn("(", str(root))
        dicts = root.as_dict()
        self.assertEqual(10, len(dicts))
        text = root.to_text()
        self.assertIn("1   1", text)
        self.assertIn('        f1', text)
        text = root.to_text(fct_width=20)
        self.assertIn('...', text)
        root.to_text(sort_key=SortKey.CUMULATIVE)
        root.to_text(sort_key=SortKey.TIME)
        self.assertRaise(lambda: root.to_text(sort_key=SortKey.NAME),
                         NotImplementedError)


if __name__ == "__main__":
    unittest.main()
