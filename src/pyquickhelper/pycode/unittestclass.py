"""
@file
@brief Overwrites unit test class with additional testing functions.

.. versionadded:: 1.5
"""
import os
import unittest
import warnings
import decimal
from .ci_helper import is_travis_or_appveyor


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
                ExtTestCase._format_str(x), ExtTestCase._format_str(y)))

    def assertLesser(self, x, y):
        """
        Checks that ``x <= y``.
        """
        if x > y:
            raise AssertionError("x > y with x={0} and y={1}".format(
                ExtTestCase._format_str(x), ExtTestCase._format_str(y)))

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

    def assertEqualNumber(self, d1, d2, **kwargs):
        """
        Checks that two numbers are equal.
        """
        from numpy import number
        if not isinstance(d1, (int, float, decimal.Decimal, number)):
            raise TypeError('d1 is not a number but {0}'.format(type(d1)))
        if not isinstance(d2, (int, float, decimal.Decimal, number)):
            raise TypeError('d2 is not a number but {0}'.format(type(d2)))
        diff = abs(float(d1 - d2))
        mi = float(min(abs(d1), abs(d2)))
        tol = kwargs.get('precision', None)
        if tol is None:
            if diff != 0:
                raise AssertionError("d1 != d2: {0} != {1}".format(d1, d2))
        else:
            if mi == 0:
                if diff > tol:
                    raise AssertionError(
                        "d1 != d2: {0} != {1} +/- {2}".format(d1, d2, tol))
            else:
                rel = diff / mi
                if rel > tol:
                    raise AssertionError(
                        "d1 != d2: {0} != {1} +/- {2}".format(d1, d2, tol))

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
                "Function '{0}' does not raise exception '{1}' but '{2}' of type '{3}'.".format(fct, exc, e, type(e)))
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
                "'{1}' does not start with '{0}'".format(sub, whole))

    def assertEndsWith(self, sub, whole):
        """
        Checks that string *sub* starts with *whole*.
        """
        if not whole.endswith(sub):
            if len(whole) > len(sub) * 2:
                whole = whole[-len(sub) * 2:]
            raise AssertionError(
                "'{1}' does not end with '{0}'".format(sub, whole))

    def assertEqual(self, a, b):
        """
        Checks that ``a == b``.
        """
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

    def assertEqualFloat(self, a, b, precision=1e-5):
        """
        Checks that ``abs(a-b) < precision``.
        """
        if min(a, b) == 0:
            d = abs(a - b)
            self.assertLesser(d, precision)
        else:
            r = float(abs(a - b)) / min(a, b)
            self.assertLesser(r, precision)

    def assertCallable(self, fct):
        """
        Checks that *fct* is callable.
        """
        if not callable(fct):
            raise AssertionError("fct is not callable: {0}".format(type(fct)))

    def assertEqualDict(self, a, b):
        """
        Checks that ``a == b``.
        """
        if not isinstance(a, dict):
            raise TypeError('a is not dict but {0}'.format(type(a)))
        if not isinstance(b, dict):
            raise TypeError('b is not dict but {0}'.format(type(b)))
        rows = []
        for key in sorted(b):
            if key not in a:
                rows.append("** Added key '{0}' in b".format(key))
            else:
                if a[key] != b[key]:
                    rows.append(
                        "** Value != for key '{0}': != {1}".format(key, [a[key], "***", b[key]]))
        for key in sorted(a):
            if key not in b:
                rows.append("** Removed key '{0}' in a".format(key))
        if len(rows) > 0:
            raise AssertionError(
                "Dictionaries are different\n{0}".format('\n'.join(rows)))

    def assertEmpty(self, a):
        """
        Checks that ``a`` is empty or *None*.
        """
        if a is None:
            return
        try:
            nb = len(a)
        except Exception:
            return
        if nb == 0:
            return
        raise AssertionError('object is a container and is not empty\n{0}'.format(
            '\n'.join(str(_) for _ in a)))


def skipif_appveyor(msg):
    """
    Skips a unit test if it runs on :epkg:`appveyor`.

    .. versionadded:: 1.6
    """
    if is_travis_or_appveyor() != 'appveyor':
        return lambda x: x
    msg = 'Test does not work on appveyor due to: ' + msg
    return unittest.skip(msg)


def skipif_travis(msg):
    """
    Skips a unit test if it runs on :epkg:`travis`.

    .. versionadded:: 1.6
    """
    if is_travis_or_appveyor() != 'travis':
        return lambda x: x
    msg = 'Test does not work on travis due to: ' + msg
    return unittest.skip(msg)


def skipif_circleci(msg):
    """
    Skips a unit test if it runs on :epkg:`circleci`.

    .. versionadded:: 1.6
    """
    if is_travis_or_appveyor() != 'circleci':
        return lambda x: x
    msg = 'Test does not work on circleci due to: ' + msg
    return unittest.skip(msg)
