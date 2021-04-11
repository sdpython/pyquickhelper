"""
@brief      test log(time=0s)
"""

import os
import unittest
from pyquickhelper.pycode import check_pep8, ExtTestCase


class TestCodeStyle(ExtTestCase):
    """Test style."""

    def test_style_src(self):
        thi = os.path.abspath(os.path.dirname(__file__))
        src_ = os.path.normpath(os.path.join(
            thi, "..", "..", "python3_module_template"))
        check_pep8(src_,
                   skip=["myexampleb.py:61: C0123", "myexampleb.py:59: C0123"])

    def test_style_test(self):
        thi = os.path.abspath(os.path.dirname(__file__))
        test = os.path.normpath(os.path.join(thi, "..", ))
        check_pep8(test,
                   pylint_ignore=('C0103', 'C1801', 'R0201', 'R1705', 'W0108', 'W0613',
                                  'C0111'),
                   skip=[])


if __name__ == "__main__":
    unittest.main()
