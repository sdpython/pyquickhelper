"""
@file
@brief Overwrites unit test class with additional testing functions.

.. versionadded:: 1.5
"""
import os
import unittest


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

    def assertRaise(self, fct, exc=None):
        """
        Checks that function *fct* with no parameter
        raises an exception of a given type.
        """
        try:
            fct()
        except Exception as e:
            if exc is None:
                return
            elif isinstance(e, exc):
                return
            raise AssertionError(
                "Function '{0}' does not raise exception '{1}' but '{2}'.".format(fct, exc, e))
        raise AssertionError(
            "Function '{0}' does not raise exception.".format(fct))
