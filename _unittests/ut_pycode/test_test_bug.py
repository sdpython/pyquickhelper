"""
@brief      test tree node (time=5s)
"""


import sys
import os
import unittest
import warnings

from pyquickhelper.pycode import ExtTestCase
from pyquickhelper.pycode.utils_tests_private import get_test_file


class TestTestBug(ExtTestCase):

    def test_get_test_file(self):
        this = os.path.abspath(os.path.dirname(__file__))
        this = os.path.normpath(os.path.join(this, "..", ".."))
        tests = get_test_file("test_*", this)
        self.assertNotEmpty(tests)


if __name__ == "__main__":
    unittest.main()
