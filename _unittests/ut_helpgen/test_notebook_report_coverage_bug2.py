"""
@brief      test log(time=9s)
"""

import sys
import os
import unittest

from pyquickhelper.pycode import get_temp_folder
from pyquickhelper.loghelper import fLOG
from pyquickhelper.helpgen.process_notebooks import build_all_notebooks_coverage


class TestNotebookReportCoverageBug2(unittest.TestCase):

    def test_notebook_report_coverage_bug2(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        temp = get_temp_folder(__file__, "temp_notebook_report_coverage_bug2")
        data = os.path.join(temp, "..", "data",
                            "dump.notebook.pyquickhelper_bug.txt")
        # to shrink the report
        do = True
        if do:
            import pandas
            df = pandas.read_csv(data, encoding="utf-8",
                                 low_memory=True, sep="\t")
            df = df.drop("output", axis=1)
            df["output"] = ""
            df.to_csv(data + ".csv", index=False, encoding="utf-8", sep="\t")
        fold = os.path.join(temp, "..", "..", "..", "_doc", "notebooks")
        nbs = [_ for _ in os.listdir(
            fold) if os.path.splitext(_)[-1] == ".ipynb"]
        if len(nbs) == 0:
            raise ValueError("No notebook to report.")
        nbs = [os.path.normpath(os.path.join(fold, _)) for _ in nbs]
        out = os.path.join(temp, "coverage.rst")
        df = build_all_notebooks_coverage(
            nbs, out, "pyquickhelper", dump=data, fLOG=fLOG)

        note = df.notebooks.dropna()
        if note.shape[0] < df.shape[0]:
            fLOG(df)
            raise AssertionError(f"nan values: {note.shape[0]} < {df.shape[0]}")
        self.assertTrue(note.shape[0] > 0)


if __name__ == "__main__":
    unittest.main()
