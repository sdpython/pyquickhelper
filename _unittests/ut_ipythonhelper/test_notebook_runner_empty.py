"""
@brief      test log(time=3s)
"""

import sys
import os
import unittest

from pyquickhelper.ipythonhelper import run_notebook
from pyquickhelper.pycode import get_temp_folder
from pyquickhelper.loghelper import fLOG
from pyquickhelper.pycode import is_travis_or_appveyor


class TestNotebookRunnerEmpty (unittest.TestCase):

    def test_notebook_runner_empty(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        temp = get_temp_folder(__file__, "temp_notebook_empty")
        nbfile = os.path.join(
            temp,
            "..",
            "data",
            "td2a_cenonce_session_4B.ipynb")
        assert os.path.exists(nbfile)
        addpath = os.path.normpath(os.path.join(temp, "..", "..", "..", "src"))
        assert os.path.exists(addpath)

        outfile = os.path.join(temp, "out_notebook.ipynb")
        assert not os.path.exists(outfile)
        out = run_notebook(nbfile, working_dir=temp, outfilename=outfile,
                           additional_path=[addpath])
        fLOG(out)
        assert os.path.exists(outfile)
        assert "No module named 'pyquickhelper'" not in out


if __name__ == "__main__":
    unittest.main()
