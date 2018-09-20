"""
@brief      test log(time=8s)
@author     Xavier Dupre
"""

import sys
import os
import unittest
import shutil
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
from src.pyquickhelper.pycode import process_standard_options_for_setup_help, get_temp_folder
from src.pyquickhelper.texthelper import compare_module_version
from src.pyquickhelper.texthelper.version_helper import numeric_module_version
from src.pyquickhelper.pycode.setup_helper import clean_notebooks_for_numbers


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

    def test_numeric_module_version(self):
        self.assertEqual(numeric_module_version((4, 5)), (4, 5))
        self.assertEqual(numeric_module_version("4.5.e"), (4, 5, 'e'))
        self.assertEqual(compare_module_version(("4.5.e"), (4, 5, 'e')), 0)
        self.assertEqual(compare_module_version(("4.5.e"), None), -1)
        self.assertEqual(compare_module_version(None, ("4.5.e")), 1)
        self.assertEqual(compare_module_version(None, None), 0)
        self.assertEqual(compare_module_version(
            ("4.5.e"), (4, 5, 'e', 'b')), -1)

    def test_clean_notebooks_for_numbers(self):
        temp = get_temp_folder(__file__, "temp_clean_notebooks_for_numbers")
        nb = os.path.join(temp, "..", "data", "notebook_with_svg.ipynb")
        fold = os.path.join(temp, '_doc', 'notebooks')
        self.assertNotExists(fold)
        os.makedirs(fold)
        shutil.copy(nb, fold)
        res = clean_notebooks_for_numbers(temp)
        self.assertEqual(len(res), 1)
        with open(res[0], 'r') as f:
            content = f.read()
        self.assertIn('"execution_count": 1,', content)


if __name__ == "__main__":
    unittest.main()
