"""
@brief      test tree node (time=5s)
"""
import unittest
from pyquickhelper.pycode import ExtTestCase
from pyquickhelper.pycode.unittest_assert import getstate


class AAAA:

    def __init__(self):
        self.g = ['h']


class AAAA2:

    def __init__(self):
        self.g = ['H']


class AAA:

    def __init__(self):
        self.glist = [AAAA()]
        self.gtuple = (AAAA2(), )
        self.gdict = {0: AAAA()}


class BBB:

    def __init__(self):
        pass

    def __getstate__(self):
        raise NotImplementedError()


class TestUnitTestAssert(ExtTestCase):

    def test_getstate(self):
        d = dict(a=1, b=2)
        r = getstate(d)
        self.assertEqual(d, r)

        d = ['R', 1]
        r = getstate(d)
        self.assertEqual(d, r)

        d = ('R', 1)
        r = getstate(d)
        self.assertEqual(d, r)

        d = {'R', 1}
        r = getstate(d)
        self.assertEqual(d, r)

        d = None
        r = getstate(d)
        self.assertEqual(d, r)

    def test_getstate_recursion(self):
        d = dict(a=1, b=2)
        d['d'] = d
        r = getstate(d)
        del r['d']
        del d['d']
        self.assertEqual(d, r)

    def test_getstate2(self):
        d = dict(a=1, b=2, c=[5])
        r = getstate(d)
        self.assertEqual(d, r)

        d = ['R', 1, (6,)]
        r = getstate(d)
        self.assertEqual(d, r)

        d = ('R', 1, {1: 2})
        r = getstate(d)
        self.assertEqual(d, r)

    def test_getstate_exc(self):
        d = [BBB()]
        self.assertRaise(lambda: getstate(d), NotImplementedError)

    def test_getstate_obj(self):
        d = [AAA()]
        r = getstate(d)
        expected = [{'glist': [{'g': ['h']}],
                     'gtuple': ({'g': ['H']},),
                     'gdict': {0: {'g': ['h']}}}]
        self.assertEqual(expected, r)


if __name__ == "__main__":
    TestUnitTestAssert().test_getstate_obj()
    unittest.main()
