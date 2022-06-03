"""
@brief      test tree node (time=1s)
"""

import sys
import os
import unittest
from pyquickhelper.pycode import ExtTestCase
from pyquickhelper.loghelper.flog import IsEmptyString
from pyquickhelper.loghelper.pqh_exception import PQHException
from pyquickhelper.loghelper.os_helper import get_machine


class TestMissing(ExtTestCase):

    def test_exception(self):
        try:
            raise PQHException("error", True)
        except PQHException:
            pass

    def test_is_missing(self):
        assert IsEmptyString("")
        assert IsEmptyString(None)
        assert not IsEmptyString("-")

    def test_get_machine(self):
        self.assertIsInstance(get_machine(), str)


if __name__ == "__main__":
    unittest.main()
