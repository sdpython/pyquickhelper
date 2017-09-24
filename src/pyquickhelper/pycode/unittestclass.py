"""
@file
@brief Overwrites unit test class with additional testing functions.

.. versionadded:: 1.5
"""
import os
import unittest
import warnings


class ExtTestCase(unittest.TestCase):
    """
    Overwrites unit test class with additional testing functions.
    """
    @staticmethod
    def _format_str(s):
        """
        Returns ``s`` or ``'s'`` depending on the type.
        """
        if hasattr(s, "replace"):
            return "'{0}'".format(s)
        else:
            return s

    def assertNotEmpty(self, x):
        """
        Checks that *x* is not empty.
        """
        if x is None or (hasattr(x, "__len__") and len(x) == 0):
            raise AssertionError("x est empty")

    def assertGreater(self, x, y):
        """
        Checks that ``x >= y``.
        """
        if x < y:
            raise AssertionError("x < y with x={0} and y={1}".format(
                ExtTestCase._format_str(x), ExtTestCase._format_str(x)))

    def assertLesser(self, x, y):
        """
        Checks that ``x <= y``.
        """
        if x > y:
            raise AssertionError("x > y with x={0} and y={1}".format(
                ExtTestCase._format_str(x), ExtTestCase._format_str(x)))

    def assertExists(self, name):
        """
        Checks that *name* exists.
        """
        if not os.path.exists(name):
            raise FileNotFoundError("Unable to find '{0}'.".format(name))

    def assertEqualDataFrame(self, d1, d2, **kwargs):
        """
        Checks that two dataframes are equal.
        Calls :epkg:`pandas:testing:assert_frame_equal`.
        """
        from pandas.testing import assert_frame_equal
        assert_frame_equal(d1, d2, **kwargs)

    def assertEqualArray(self, d1, d2, **kwargs):
        """
        Checks that two arrays are equal.
        Calls :epkg:`numpy:`.
        """
        from numpy.testing import assert_array_equal
        assert_array_equal(d1, d2, **kwargs)

    def assertRaise(self, fct, exc=None, msg=None):
        """
        Checks that function *fct* with no parameter
        raises an exception of a given type.

        @param      fct     function to test (no parameter)
        @param      exc     exception type to catch (None for all)
        @param      msg     error message to check (None for no message to check)
        """
        try:
            fct()
        except Exception as e:
            if exc is None:
                return
            elif isinstance(e, exc):
                if msg is None:
                    return
                if msg not in str(e):
                    raise AssertionError(
                        "Function '{0}' raise exception with wrong message '{1}' (must contain '{2}').".format(fct, e, msg))
                return
            raise AssertionError(
                "Function '{0}' does not raise exception '{1}' but '{2}'.".format(fct, exc, e))
        raise AssertionError(
            "Function '{0}' does not raise exception.".format(fct))

    def assertStartsWith(self, sub, whole):
        """
        Checks that string *sub* starts with *whole*.
        """
        if not whole.startswith(sub):
            if len(whole) > len(sub) * 2:
                whole = whole[:len(sub) * 2]
            raise AssertionError(
                "'{0}' does not start '{1}'".format(sub, whole))

    def assertEndsWith(self, sub, whole):
        """
        Checks that string *sub* starts with *whole*.
        """
        if not whole.endswith(sub):
            if len(whole) > len(sub) * 2:
                whole = whole[-len(sub) * 2:]
            raise AssertionError("'{0}' does not end '{1}'".format(sub, whole))

    def assertEqual(self, a, b):
        try:
            unittest.TestCase.assertEqual(self, a, b)
        except ValueError as e:
            if "The truth value of a DataFrame is ambiguous" in str(e):
                with warnings.catch_warnings():
                    warnings.filterwarnings("ignore", category=ImportWarning)
                    import pandas
                if isinstance(a, pandas.DataFrame) and isinstance(b, pandas.DataFrame):
                    self.assertEqualDataFrame(a, b)
                    return
            raise e
