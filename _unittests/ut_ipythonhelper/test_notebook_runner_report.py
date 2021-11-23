"""
@brief      test log(time=7s)
"""
import os
import unittest
import pyquickhelper
from pyquickhelper.ipythonhelper import notebook_coverage


class TestNotebookRunnerReport (unittest.TestCase):

    def test_notebook_runner_report(self):
        this = os.path.abspath(os.path.dirname(__file__))
        dump = os.path.join(this, "data", "dump.notebook.pyquickhelper.txt")
        cov = notebook_coverage(pyquickhelper, dump=dump)
        if len(cov) == 0:
            raise Exception("dataframe cannot be empty")
        if len(cov) <= 9:
            raise Exception("too few found notebooks")

        if cov.shape[0] != 16:
            raise AssertionError("NB={0}\n----\n{1}".format(cov.shape, cov))
        self.assertIn("last_name", cov.columns)
        cols = ['notebooks', 'last_name', 'date', 'etime',
                'nbcell', 'nbrun', 'nbvalid', 'success', 'time']
        subcov = cov[cols].copy()
        dropna = subcov.dropna()
        self.assertEqual(dropna.shape[1], 9)


if __name__ == "__main__":
    unittest.main()
