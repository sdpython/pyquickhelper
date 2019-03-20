"""
@brief      test log(time=9s)
"""

import sys
import os
import unittest

from pyquickhelper.pycode import get_temp_folder
from pyquickhelper.loghelper import fLOG
from pyquickhelper.helpgen.process_notebooks import build_all_notebooks_coverage


class TestNotebookReportCoverage(unittest.TestCase):

    def test_notebook_report_coverage(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        temp = get_temp_folder(__file__, "temp_notebook_report_coverage")
        data = os.path.join(temp, "..", "data",
                            "dump.notebook.pyquickhelper.txt")
        fold = os.path.join(temp, "..", "..", "..", "_doc", "notebooks")
        nbs = [_ for _ in os.listdir(
            fold) if os.path.splitext(_)[-1] == ".ipynb"]
        if len(nbs) == 0:
            raise ValueError("No notebook to report.")
        nbs = [os.path.normpath(os.path.join(fold, _)) for _ in nbs]
        out = os.path.join(temp, "coverage.rst")
        build_all_notebooks_coverage(
            nbs, out, "pyquickhelper", dump=data, fLOG=fLOG, too_old=3000)


if __name__ == "__main__":
    unittest.main()
