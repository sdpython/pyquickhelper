"""
@brief      test log(time=1s)

You should indicate a time in seconds. The program ``run_unittests.py``
will sort all test files by increasing time and run them.
"""

import unittest
from pyquickhelper.pycode import ExtTestCase

from python3_module_template.subproject.myexample import myclass
from python3_module_template.subproject.myexampleb import myclassb
from python3_module_template.subproject2.myexample2 import myclass2


class TestExample(ExtTestCase):
    """Example of a test."""

    def test_split_cmp_command(self):
        my = myclass(4)
        r = my.get_value(5)
        ex = 20
        if r != ex:
            raise Exception("we expect %f, not %f" % (ex, r))
        my2 = myclass2(5)
        my3 = myclassb(4)
        self.assertTrue(my2 is not None)
        self.assertTrue(my3 is not None)
        mul = my2.get_value(3)
        self.assertEqual(mul, 15)


if __name__ == "__main__":
    unittest.main()
