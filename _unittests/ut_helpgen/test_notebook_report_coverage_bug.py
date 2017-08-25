"""
@brief      test log(time=9s)
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

from src.pyquickhelper.pycode import get_temp_folder
from src.pyquickhelper.loghelper import fLOG
from src.pyquickhelper.helpgen.process_notebooks import build_all_notebooks_coverage


class TestNotebookReportCoverageBug(unittest.TestCase):

    def test_notebook_report_coverage_bug(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        temp = get_temp_folder(__file__, "temp_notebook_report_coverage_bug")
        data = os.path.join(temp, "..", "data",
                            "dump.notebook.ensae_projects.txt")
        # to shrink the report
        if False:
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
            raise Exception("nan values: {0} < {1}".format(
                note.shape[0], df.shape[0]))
        self.assertTrue(note.shape[0] > 0)


if __name__ == "__main__":
    unittest.main()