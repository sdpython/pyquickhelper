"""
@brief      test tree node (time=5s)
"""
import sys
import os
import unittest
import warnings
import numpy
import pandas
from pyquickhelper.pycode import (
    ExtTestCase, unittest_require_at_least, ignore_warnings, testlog,
    assert_almost_equal_detailed)
from pyquickhelper.pandashelper import df2rst
from pyquickhelper import __file__ as rootfile


class TestExtTestCase(ExtTestCase):

    def test_files(self):
        self.assertExists(__file__)
        self.assertRaise(lambda: self.assertExists(__file__ + ".k"),
                         FileNotFoundError)

    def test_files_msg(self):
        self.assertExists(__file__)
        self.assertRaise(lambda: self.assertExists(__file__ + ".k"),
                         FileNotFoundError, "Unable to find")

    def test_assertRaise(self):
        def fraise(e):
            raise e
        self.assertRaise(lambda: fraise(TypeError()), TypeError)
        self.assertRaise(lambda: self.assertRaise(
            lambda: fraise(TypeError()), ValueError), AssertionError)

    def test_greater(self):
        self.assertGreater("c", "b")
        self.assertGreater("c", "c")
        self.assertRaise(lambda: self.assertGreater(
            "c", "c", strict=True), AssertionError)
        self.assertRaise(lambda: self.assertGreater("a", "b"), AssertionError)

    def test_lesser(self):
        self.assertLesser("a", "b")
        self.assertLesser("a", "a")
        self.assertRaise(lambda: self.assertLesser(
            "a", "a", strict=True), AssertionError)
        self.assertRaise(lambda: self.assertLesser("c", "b"), AssertionError)

    def test_df(self):
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=ImportWarning)
            from pandas import DataFrame
        df = DataFrame(data=dict(a=["a"]))
        df1 = DataFrame(data=dict(a=["a"]))
        df2 = DataFrame(data=dict(a=["b"]))
        self.assertEqualDataFrame(df, df1)
        self.assertEqual(None, None)
        self.assertRaise(lambda: self.assertEqualDataFrame(df, df2),
                         AssertionError)
        self.assertRaise(lambda: self.assertEqual(df, None),
                         AssertionError)
        self.assertRaise(lambda: self.assertEqual(None, df),
                         AssertionError)
        self.assertEqual(df, df1)
        self.assertRaise(lambda: self.assertNotEqual(df, df1),
                         AssertionError)
        self.assertRaise(lambda: self.assertEqual(df, df2),
                         AssertionError)
        df["new"] = 1
        self.assertNotEqual(df, df1)

    def test_arr(self):
        from numpy import array
        df = array([[0, 1], [1, 2]])
        df1 = array([[0, 1], [1, 2]])
        df2 = array([[0, 1], [3, 2]])
        self.assertEqualArray(df, df1)
        self.assertEqualArray(None, None)
        self.assertRaise(lambda: self.assertEqualArray(df, df2),
                         AssertionError)
        self.assertRaise(lambda: self.assertEqualArray(df, None),
                         AssertionError)
        self.assertRaise(lambda: self.assertEqualArray(None, df),
                         AssertionError)

    def test_nan(self):
        from numpy import array, nan
        df = array([[nan, 1], [1, 2]])
        df1 = array([[0, 1], [1, 2]])
        self.assertHasNoNan(df1)
        self.assertRaise(lambda: self.assertHasNoNan(None), AssertionError)
        self.assertRaise(lambda: self.assertHasNoNan(df), AssertionError)

    def test_arr_squeeze(self):
        from numpy import array
        df = array([[0, 1], [1, 2]])
        df1 = array([[0, 1], [1, 2]]).reshape((2, 2, 1))
        df2 = array([[0, 1], [3, 2]]).reshape((2, 2, 1))
        self.assertEqualArray(df, df1, squeeze=True)
        self.assertEqualArray(None, None)
        self.assertRaise(lambda: self.assertEqualArray(df, df2, squeeze=True),
                         AssertionError)
        self.assertRaise(lambda: self.assertEqualArray(df, None, squeeze=True),
                         AssertionError)
        self.assertRaise(lambda: self.assertEqualArray(None, df, squeeze=True),
                         AssertionError)

    def test_arr_not_equal_noe(self):
        from numpy import array
        df = array([[0, 1], [1, 2]])
        df1 = array([[0, 1], [1, 2]])
        df2 = array([[0, 1], [3, 2]])
        self.assertRaise(lambda: self.assertNotEqualArray(
            df, df1), AssertionError)
        self.assertRaise(lambda: self.assertNotEqualArray(
            None, None), AssertionError)
        self.assertNotEqualArray(df, None)
        self.assertNotEqualArray(None, df)

    def test_arr_not_equal_noe_squeeze(self):
        from numpy import array
        df = array([[0, 1], [1, 2]])
        df1 = array([[0, 1], [1, 2]]).reshape((2, 2, 1))
        df2 = array([[0, 1], [3, 2]]).reshape((2, 2, 1))
        self.assertRaise(lambda: self.assertNotEqualArray(
            df, df1, squeeze=True), AssertionError)
        self.assertRaise(lambda: self.assertNotEqualArray(
            None, None, squeeze=True), AssertionError)
        self.assertNotEqualArray(df, None, squeeze=True)
        self.assertNotEqualArray(None, df, squeeze=True)

    def test_arr_equal(self):
        from numpy import array
        df = array([[0, 1], [1, 2]])
        df1 = array([[0, 1], [1, 2]])
        df2 = array([[0, 1], [3, 2]])
        self.assertEqual(df, df1)
        self.assertRaise(lambda: self.assertEqual(df, df2),
                         AssertionError)

    def test_arr_not_equal(self):
        from numpy import array
        df = array([[0, 1], [1, 2]])
        df1 = array([[0, 1], [1, 3]])
        self.assertNotEqual(df, df1)
        self.assertRaise(lambda: self.assertNotEqual(df, df),
                         AssertionError)

    def test_str(self):
        self.assertStartsWith("a", "ab")
        self.assertRaise(lambda: self.assertNotStartsWith("a", "ab"),
                         AssertionError)
        self.assertNotStartsWith("c", "ab")
        self.assertRaise(lambda: self.assertStartsWith("ab", "a"),
                         AssertionError)
        self.assertEndsWith("a", "ba")
        self.assertRaise(lambda: self.assertNotEndsWith("a", "ba"),
                         AssertionError)
        self.assertNotEndsWith("a", "bc")
        self.assertRaise(lambda: self.assertEndsWith("ba", "a"),
                         AssertionError)
        self.assertRaise(lambda: self.assertEndsWith("ba", "a" * 100),
                         AssertionError)

    def test_not_empty(self):
        self.assertNotEmpty([0])
        self.assertEmpty(None)
        self.assertEmpty([])
        self.assertRaise(lambda: self.assertNotEmpty(None), AssertionError)
        self.assertRaise(lambda: self.assertNotEmpty([]), AssertionError)
        self.assertRaise(lambda: self.assertEmpty([0]), AssertionError)

    def test_callable(self):
        self.assertCallable(zip)
        self.assertRaise(lambda: self.assertCallable('a'), AssertionError)

    def test_assertEmpty(self):
        self.assertEmpty(None)
        self.assertEmpty([])
        self.assertEmpty({})
        self.assertRaise(lambda: self.assertEmpty(['a']), AssertionError)

    def test_assertNotEmpty(self):
        self.assertRaise(lambda: self.assertNotEmpty(None), AssertionError)
        self.assertRaise(lambda: self.assertNotEmpty([]), AssertionError)
        self.assertRaise(lambda: self.assertNotEmpty({}), AssertionError)
        self.assertNotEmpty(['a'])
        self.assertNotEmpty('a')
        self.assertNotEmpty(1)

    def test_assertEqualFloat(self):
        self.assertEqualFloat(1., 1.)
        self.assertEqualFloat(1., 1. + 1e-6)
        self.assertRaise(lambda: self.assertEqualFloat(1.1, 1.2),
                         AssertionError)

    def test_assertEqualDict(self):
        self.assertEqualDict(dict(a='a', b=1.), dict(a='a', b=1.))
        self.assertEqualDict(dict(a='a', b=1.), dict(a='a', b=1))
        self.assertRaise(lambda: self.assertEqualDict(
            dict(a='a', b=1.), dict(a='a', b=2)), AssertionError)
        self.assertRaise(lambda: self.assertEqualDict(
            dict(a='a', b=1.), dict(a='a')), AssertionError)
        self.assertRaise(lambda: self.assertEqualDict(
            dict(a='a'), dict(a='a', b=2.)), AssertionError)
        self.assertRaise(lambda: self.assertEqualDict(
            None, dict(a='a', b=2)), TypeError)
        self.assertRaise(lambda: self.assertEqualDict(
            dict(a='a', b=2), None), TypeError)

    def test_assertEqualNumber(self):
        self.assertEqualNumber(1., 1.)
        self.assertEqualNumber(1., 1. + 1e-6, precision=1e-5)
        self.assertRaise(lambda: self.assertEqualNumber(1.1, 1.2),
                         AssertionError)
        self.assertRaise(lambda: self.assertEqualNumber("1.1", 1.2),
                         TypeError)
        self.assertRaise(lambda: self.assertEqualNumber(1.1, "1.2"),
                         TypeError)

    def test_profile(self):

        def simple():
            df = pandas.DataFrame([{"A": "x", "AA": "xx", "AAA": "xxx"},
                                   {"AA": "xxxxxxx", "AAA": "xxx"}])
            return df2rst(df)

        rootrem = os.path.normpath(os.path.abspath(
            os.path.join(os.path.dirname(rootfile), '..')))
        ps, res = self.profile(
            simple, rootrem=rootrem)  # pylint: disable=W0632
        res = res.replace('\\', '/')
        self.assertIn('pyquickhelper/pandashelper/tblformat.py', res)
        self.assertNotEmpty(ps)

    def test_capture(self):
        def ok():
            print('okok')
            return 3
        res, out, err = self.capture(ok)
        self.assertIn('okok', out)
        self.assertEmpty(err)
        self.assertEqual(res, 3)

    def test_version_module(self):

        @unittest_require_at_least(pandas, '0.20')
        def zoo():
            return 3

        self.assertEqual(zoo(), 3)

        @unittest_require_at_least(pandas, '100.20')
        def zoo2():
            return 3

        try:
            zoo2()
        except Exception as e:
            self.assertIn('older than', str(e))

    @ignore_warnings(RuntimeWarning)
    def test_sparse_arr(self):
        from numpy import array
        from scipy.sparse import coo_matrix, csc_matrix, csr_matrix
        df = coo_matrix(array([[0, 1], [1, 2]]))
        df1 = coo_matrix(array([[0, 1], [1, 2]]))
        df2 = coo_matrix(array([[0, 1], [3, 2]]))
        self.assertEqualSparseArray(df, df1)
        self.assertEqualSparseArray(None, None)
        self.assertRaise(lambda: self.assertEqualSparseArray(df, df2),
                         AssertionError)
        self.assertRaise(lambda: self.assertEqualSparseArray(df, None),
                         AssertionError)
        self.assertRaise(lambda: self.assertEqualSparseArray(None, df),
                         AssertionError)

        df = csr_matrix(array([[0, 1], [1, 2]]))
        df1 = csr_matrix(array([[0, 1], [1, 2]]))
        df2 = csr_matrix(array([[0, 1], [3, 2]]))
        self.assertEqualSparseArray(df, df1)
        self.assertEqualSparseArray(None, None)
        self.assertRaise(lambda: self.assertEqualSparseArray(df, df2),
                         AssertionError)
        self.assertRaise(lambda: self.assertEqualSparseArray(df, None),
                         AssertionError)
        self.assertRaise(lambda: self.assertEqualSparseArray(None, df),
                         AssertionError)

        df = csc_matrix(array([[0, 1], [1, 2]]))
        df1 = csc_matrix(array([[0, 1], [1, 2]]))
        df2 = csc_matrix(array([[0, 1], [3, 2]]))
        self.assertEqualSparseArray(df, df1)
        self.assertEqualSparseArray(None, None)
        self.assertRaise(lambda: self.assertEqualSparseArray(df, df2),
                         AssertionError)
        self.assertRaise(lambda: self.assertEqualSparseArray(df, None),
                         AssertionError)
        self.assertRaise(lambda: self.assertEqualSparseArray(None, df),
                         AssertionError)

    @testlog(None)
    def test_testlog_none(self):
        pass

    def test_testlog_print(self):
        self.assertRaise(lambda: testlog('ttt'), ValueError)
        fct = testlog('print')
        self.assertNotEmpty(fct)
        self.assertIn('wrapper', fct.__name__)

    def test_assert_almost_equal_detailed(self):
        mat = numpy.array([[0, 1], [0, 1]])
        assert_almost_equal_detailed(mat, mat)
        mat2 = numpy.array([[0, 1], [0.5, 1]])
        try:
            assert_almost_equal_detailed(mat, mat2)
        except AssertionError as e:
            self.assertIn("ISSUE WITH ROW 1/2:0 ", str(e))
            return
        raise AssertionError("unexpected")

    def test_assert_warnings(self):
        def fw():
            warnings.warn("g", UserWarning)
        r = self.assertWarning(fw)
        self.assertEqual(len(r[1]), 1)


if __name__ == "__main__":
    unittest.main()
