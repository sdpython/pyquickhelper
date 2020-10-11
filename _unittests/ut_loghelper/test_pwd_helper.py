"""
@brief      test tree node (time=2s)
"""
import sys
import os
import unittest

from pyquickhelper.pycode import ExtTestCase
from pyquickhelper.loghelper import set_password, get_password


class TestPwdHelper(ExtTestCase):

    def test_exc(self):
        self.assertRaise(lambda: set_password(
            'pyq', 'jj', 'aa', 'keyring2'), RuntimeError)
        self.assertRaise(lambda: get_password(
            'pyq', 'jj', 'keyring2'), RuntimeError)

    def test_password(self):
        pwd = 'bibi'
        set_password('pyq', 'jj', pwd)
        pwd2 = get_password('pyq', 'jj')
        self.assertEqual(pwd, pwd2)


if __name__ == "__main__":
    unittest.main()
