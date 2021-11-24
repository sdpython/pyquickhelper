"""
@brief      test log(time=8s)
@author     Xavier Dupre
"""
import sys
import os
import unittest
import shutil
from contextlib import redirect_stdout
from io import StringIO
from pyquickhelper.pycode import ExtTestCase
from pyquickhelper.pycode import process_standard_options_for_setup_help, get_temp_folder
from pyquickhelper.texthelper import compare_module_version
from pyquickhelper.texthelper.version_helper import numeric_module_version
from pyquickhelper.pycode.setup_helper import (
    clean_notebooks_for_numbers, hash_list, process_argv_for_unittest,
    process_standard_options_for_setup)


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

    @unittest.skipIf(sys.platform != 'win32', reason="not available")
    def test_process_standard_options_for_setup(self):
        temp = get_temp_folder(
            __file__, "temp_process_standard_options_for_setup")
        os.mkdir(os.path.join(temp, '_unittests'))
        f = StringIO()
        with redirect_stdout(f):
            process_standard_options_for_setup(
                ['build_script'], file_or_folder=temp, project_var_name="debug",
                fLOG=print)
        text = f.getvalue()
        self.assertIn('[process_standard_options_for_setup]', text)
        self.assertExists(os.path.join(temp, 'bin'))

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

    def test_hash_list(self):
        li = [4, '5']
        res = hash_list(li)
        self.assertEqual(res, "1402b9d4")
        li = []
        res = hash_list(li)
        self.assertEqual(res, "d41d8cd9")

    def test_process_argv_for_unittest(self):
        li = ['unittests', '-d', '5']
        res = process_argv_for_unittest(li, None)
        self.assertNotEmpty(res)
        li = ['unittests']
        res = process_argv_for_unittest(li, None)
        self.assertEmpty(res)
        li = ['unittests', '-e', '.*']
        res = process_argv_for_unittest(li, None)
        self.assertNotEmpty(res)
        li = ['unittests', '-g', '.*']
        res = process_argv_for_unittest(li, None)
        self.assertNotEmpty(res)
        li = ['unittests', '-f', 'test.py']
        res = process_argv_for_unittest(li, None)
        self.assertNotEmpty(res)


if __name__ == "__main__":
    unittest.main()
