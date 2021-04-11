"""
@brief      test log(time=1s)

You should indicate a time in seconds. The program ``run_unittests.py``
will sort all test files by increasing time and run them.
"""

import unittest
from pyquickhelper.pycode import ExtTestCase

from python3_module_template.subproject.myexampleb import onefunction


class TestExample(ExtTestCase):
    """Third  example of a test."""

    def test_onefunction(self):
        self.assertTrue(onefunction(3, 4), 7)
        with self.assertRaises(TypeError):
            onefunction(3.3, 4)


if __name__ == "__main__":
    unittest.main()
