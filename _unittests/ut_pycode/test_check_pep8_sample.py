"""
@brief      test tree node (time=15s)
"""


import sys
import os
import unittest

try:
    import src
except ImportError:
    path_ = os.path.normpath(
        os.path.abspath(
            os.path.join(
                os.path.split(__file__)[0],
                "..",
                "..")))
    if path_ not in sys.path:
        sys.path.append(path_)
    import src

from src.pyquickhelper.loghelper import fLOG
from src.pyquickhelper.pycode import check_pep8, ExtTestCase
from src.pyquickhelper.pycode.utils_tests_helper import PEP8Exception


class TestCheckPep8Sample(ExtTestCase):

    def line_too_long(self):
        """Line too long                                                                                                                                      ...."""

    def line_too_long_link(self):
        """Line too long                                                                                                                                      ....>`_"""

    def unused_var(self):
        aa = 5

    def undeclared_var(self):
        aa + 5

    def test_unused_variable(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        this = os.path.abspath(os.path.dirname(__file__))

        def check_pep8_one_file():
            check_pep8(this, fLOG=fLOG, max_line_length=150, recursive=False,
                       pattern="test_check_pep8_sample.py")

        def check_pep8_error_file():
            check_pep8(this, fLOG=fLOG, recursive=False,
                       pylint_ignore=('C0111', 'R0201', 'C0103'),
                       pattern="test_check_pep8_sample.py",
                       skip=["test_check_pep8_sample.py:30",
                             "test_check_pep8_sample.py:33",
                             "Unused import src"])

        self.assertRaise(check_pep8_one_file, PEP8Exception,
                         "line too long (165 > 150 characters)")
        self.assertRaise(check_pep8_one_file, PEP8Exception,
                         "F[ECL1] line too long (link) 169 > 150")
        self.assertRaise(check_pep8_error_file, PEP8Exception,
                         "E0602: Undefined variable 'aa'")
        self.assertRaise(check_pep8_error_file, PEP8Exception,
                         "W0612: Unused variable 'aa'")
        self.assertRaise(check_pep8_error_file, PEP8Exception,
                         "W0104: Statement seems to have no effect")

        check_pep8(this, fLOG=fLOG, max_line_length=170, recursive=False,
                   pylint_ignore=('C0111', 'R0201', 'C0103'),
                   pattern="test_check_pep8_sample.py",
                   skip=["test_check_pep8_sample.py:373: [E731]",
                         "test_check_pep8_sample.py:36",
                         "test_check_pep8_sample.py:39",
                         "test_check_pep8_sample.py:11",
                         "test_check_pep8_sample.py:40: E0602",
                         "test_check_pep8_sample.py:40: W0104",
                         "test_check_pep8_sample.py:37: W0612",
                         ])


if __name__ == "__main__":
    unittest.main()
