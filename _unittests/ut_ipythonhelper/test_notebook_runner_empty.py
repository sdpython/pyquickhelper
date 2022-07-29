"""
@brief      test log(time=3s)
"""
import os
import unittest
from pyquickhelper.ipythonhelper import run_notebook
from pyquickhelper.pycode import (
    get_temp_folder, ExtTestCase, ignore_warnings)
from pyquickhelper.loghelper import fLOG
from pyquickhelper.pycode import is_travis_or_appveyor


class TestNotebookRunnerEmpty(ExtTestCase):

    @ignore_warnings((DeprecationWarning, RuntimeWarning))
    def test_notebook_runner_empty(self):
        temp = get_temp_folder(__file__, "temp_notebook_empty")
        nbfile = os.path.join(
            temp, "..", "data",
            "td2a_cenonce_session_4B.ipynb")
        self.assertExists(nbfile)
        addpath = os.path.normpath(os.path.join(temp, "..", "..", "..", "src"))
        self.assertExists(addpath)

        outfile = os.path.join(temp, "out_notebook.ipynb")
        self.assertNotExists(outfile)
        out = run_notebook(nbfile, working_dir=temp, outfilename=outfile,
                           additional_path=[addpath])
        self.assertExists(outfile)
        self.assertNotIn("No module named 'pyquickhelper'", out)


if __name__ == "__main__":
    unittest.main()
