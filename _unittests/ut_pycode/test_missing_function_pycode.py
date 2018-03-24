"""
@brief      test log(time=8s)
@author     Xavier Dupre
"""

import sys
import os
import unittest
from contextlib import redirect_stdout
try:
    from io import StringIO
except ImportError:
    from StringIO import StringIO


try:
    import src
except ImportError:
    path = os.path.normpath(
        os.path.abspath(
            os.path.join(
                os.path.split(__file__)[0],
                "..",
                "..")))
    if path not in sys.path:
        sys.path.append(path)
    import src

from src.pyquickhelper.pycode import ExtTestCase
from src.pyquickhelper.pycode import process_standard_options_for_setup_help


class TestMissingFunctionsPycode(ExtTestCase):

    def test_process_standard_options_for_setup_help(self):
        f = StringIO()
        with redirect_stdout(f):
            process_standard_options_for_setup_help('--help-commands')
        self.assertIn('Commands processed by pyquickhelper:', f.getvalue())
        f = StringIO()
        with redirect_stdout(f):
            process_standard_options_for_setup_help(['--help', 'unittests'])
        self.assertIn('-f file', f.getvalue())
        f = StringIO()
        with redirect_stdout(f):
            process_standard_options_for_setup_help(['--help', 'clean_space'])
        self.assertIn('clean unnecessary spaces', f.getvalue())


if __name__ == "__main__":
    unittest.main()
