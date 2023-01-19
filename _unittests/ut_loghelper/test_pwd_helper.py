"""
@brief      test tree node (time=2s)
"""
import sys
import os
import unittest

from pyquickhelper.pycode import (
    ExtTestCase, skipif_appveyor, skipif_travis, skipif_circleci,
    skipif_azure)
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
    @skipif_azure('stuck')
    def test_password_keyring(self):
        pwd = 'bibi'
        try:
            set_password('pyq', 'jj', pwd, lib='keyring')
        except Exception as e:
            if "Prompt dismissed" in str(e):
                return
            if "Inappropriate ioctl for device" in str(e):
                return
            raise AssertionError(f"Failing due to {e}.") from e
        pwd2 = get_password('pyq', 'jj', lib='keyring')
        self.assertEqual(pwd, pwd2)

    @skipif_appveyor('stuck')
    @skipif_travis('stuck')
    @skipif_circleci('stuck')
    @skipif_azure('stuck')
    def test_password_cryptfile(self):
        os.environ['UTTESTPYQ'] = 'bypass'
        pwd = 'bibi'
        set_password('pyq', 'jj', pwd, env='UTTESTPYQ')
        pwd2 = get_password('pyq', 'jj', env='UTTESTPYQ')
        self.assertEqual(pwd, pwd2)


if __name__ == "__main__":
    unittest.main()
