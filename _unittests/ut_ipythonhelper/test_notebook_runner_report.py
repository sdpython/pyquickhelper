"""
@brief      test log(time=6s)
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

from src.pyquickhelper.ipythonhelper import notebook_coverage
from src.pyquickhelper.loghelper import fLOG
from src.pyquickhelper.pycode import is_travis_or_appveyor


class TestNotebookRunnerReport (unittest.TestCase):

    def test_notebook_runner_report(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        if is_travis_or_appveyor():
            exp = 0
        else:
            exp = 1

        this = os.path.abspath(os.path.dirname(__file__))
        dump = os.path.join(this, "data", "dump.notebook.pyquickhelper.txt")
        cov = notebook_coverage(src.pyquickhelper, dump=dump)
        if len(cov) == 0:
            raise Exception("dataframe cannot be empty")
        if len(cov) <= 9:
            raise Exception("too few found notebooks")

        self.assertEqual(cov.shape[1], 12)
        cols = ['notebooks', 'last_name', 'date', 'etime',
                'nbcell', 'nbrun', 'nbvalid', 'success', 'time']
        subcov = cov[cols].copy()
        dropna = subcov.dropna()
        self.assertEqual(dropna.shape, (exp, 9))


if __name__ == "__main__":
    unittest.main()
