"""
@brief      test log(time=1s)

You should indicate a time in seconds. The program ``run_unittests.py``
will sort all test files by increasing time and run them.
"""

import unittest
from pyquickhelper.pycode import ExtTestCase

from python3_module_template.subproject.myexampleb import myclassb
from python3_module_template.subproject2.myexample2 import myclass2
from python3_module_template import _setup_hook


class TestExampleExt(ExtTestCase):
    """Second example of a test."""

    def test_static(self):
        self.assertTrue(myclass2.static_example() is not None)
        cl = myclass2(1)
        self.assertTrue(cl.property_example is not None)

    def test_hook(self):
        _setup_hook()

    def test_myclassb(self):
        b = myclassb(1)
        c = b.method_napoleon(1, 2)
        self.assertEqual(c, 4)


if __name__ == "__main__":
    unittest.main()
