"""
@brief      test tree node (time=2s)
"""
import sys
import os
import unittest

from pyquickhelper.pycode import (
    ExtTestCase, skipif_appveyor, skipif_travis, skipif_circleci)
from pyquickhelper.loghelper import set_password, get_password


class TestPwdHelper(ExtTestCase):

    def test_exc(self):
        self.assertRaise(lambda: set_password(
            'pyq', 'jj', 'aa', 'keyring2'), RuntimeError)
        self.assertRaise(lambda: get_password(
            'pyq', 'jj', 'keyring2'), RuntimeError)

    @skipif_appveyor('stuck')
    @skipif_travis('stuck')
    @skipif_circleci('stuck')
    def test_password(self):
        pwd = 'bibi'
        set_password('pyq', 'jj', pwd)
        pwd2 = get_password('pyq', 'jj')
        self.assertEqual(pwd, pwd2)


if __name__ == "__main__":
    unittest.main()
