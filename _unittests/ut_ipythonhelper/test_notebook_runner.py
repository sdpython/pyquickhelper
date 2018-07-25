"""
@brief      test log(time=7s)
"""

import sys
import os
import unittest


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

from src.pyquickhelper.ipythonhelper.notebook_helper import install_python_kernel_for_unittest
from src.pyquickhelper.ipythonhelper import run_notebook, NotebookError
from src.pyquickhelper.pycode import get_temp_folder
from src.pyquickhelper.pycode import is_travis_or_appveyor, ExtTestCase


class TestNotebookRunner(ExtTestCase):

    def test_notebook_runner(self):
        temp = get_temp_folder(__file__, "temp_notebook")
        nbfile = os.path.join(temp, "..", "data", "simple_example.ipynb")
        self.assertExists(nbfile)
        addpath = os.path.normpath(os.path.join(temp, "..", "..", "..", "src"))
        self.assertExists(addpath)

        outfile = os.path.join(temp, "out_notebook.ipynb")
        self.assertNotExists(outfile)

        if sys.version_info[0] == 2:
            return

        kernel_name = None if is_travis_or_appveyor() is not None else install_python_kernel_for_unittest(
            "pyquickhelper")
        stat, out = run_notebook(nbfile, working_dir=temp, outfilename=outfile,
                                 additional_path=[addpath],
                                 kernel_name=kernel_name)
        self.assertExists(outfile)
        self.assertNotIn("No module named 'pyquickhelper'", out)
        self.assertIn("datetime.datetime(2015, 3, 2", out)
        self.assertIsInstance(stat, dict)

    def test_notebook_runner_exc(self):
        temp = get_temp_folder(__file__, "temp_notebook")
        nbfile = os.path.join(temp, "..", "data", "simple_example_exc.ipynb")
        self.assertExists(nbfile)
        addpath = os.path.normpath(os.path.join(temp, "..", "..", "..", "src"))
        self.assertExists(addpath)

        outfile = os.path.join(temp, "out_notebook.ipynb")
        self.assertNotExists(outfile)

        if sys.version_info[0] == 2:
            return

        kernel_name = None if is_travis_or_appveyor() is not None else install_python_kernel_for_unittest(
            "pyquickhelper")
        try:
            run_notebook(nbfile, working_dir=temp, outfilename=outfile,
                         additional_path=[addpath],
                         kernel_name=kernel_name)
        except NotebookError as e:
            self.assertIn("name 'str2datetimes' is not defined", str(e))


if __name__ == "__main__":
    unittest.main()
