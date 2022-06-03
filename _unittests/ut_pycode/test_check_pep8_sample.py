"""
@brief      test tree node (time=15s)
"""
import os
import unittest
import sys
from pyquickhelper.pycode import check_pep8, ExtTestCase
from pyquickhelper.pycode.utils_tests_helper import PEP8Exception


class TestCheckPep8Sample(ExtTestCase):

    def line_too_long(self):
        """Line too long                                                                                                                                      ...."""

    def line_too_long_link(self):
        """Line too long                                                                                                                                      ....>`_"""

    def unused_var(self):
        aa = 5  # pylint: disable=W0612

    def undeclared_var(self):
        aa + 5  # pylint: disable=E0602, W0104

    @unittest.skipIf(sys.version_info[:2] <= (3, 6),
                     reason="pylint not available in the last version")
    def test_unused_variable(self):
        this = os.path.abspath(os.path.dirname(__file__))

        def check_pep8_one_file():
            check_pep8(this, max_line_length=150, recursive=False,
                       neg_pattern="##",
                       pattern="test_check_pep8_sample.py")

        def check_pep8_error_file():
            check_pep8(this, recursive=False,
                       pylint_ignore=('C0111', 'C0103'),
                       pattern="test_check_pep8_sample.py",
                       neg_pattern="##",
                       skip=["test_check_pep8_sample.py:15",
                             "test_check_pep8_sample.py:18"])

        self.assertRaise(check_pep8_one_file, PEP8Exception,
                         "line too long (165 > 150 characters)")
        self.assertRaise(check_pep8_one_file, PEP8Exception,
                         "F[ECL1] line too long (link) 169 > 150")

        check_pep8(this, max_line_length=170, recursive=False,
                   pylint_ignore=('C0111', 'C0103'),
                   pattern="test_check_pep8_sample.py",
                   neg_pattern="##",
                   skip=["test_check_pep8_sample.py:373: [E731]",
                         "test_check_pep8_sample.py:35",
                         "test_check_pep8_sample.py:39",
                         "test_check_pep8_sample.py:11",
                         "test_check_pep8_sample.py:40: E0602",
                         "test_check_pep8_sample.py:40: W0104",
                         "test_check_pep8_sample.py:37: W0612",
                         ])


if __name__ == "__main__":
    unittest.main()
