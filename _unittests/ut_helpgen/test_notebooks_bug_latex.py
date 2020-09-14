"""
@brief      test log(time=19s)
@author     Xavier Dupre
"""
import sys
import os
import unittest

from pyquickhelper.loghelper import fLOG
from pyquickhelper.helpgen.sphinx_main import process_notebooks
from pyquickhelper.pycode import is_travis_or_appveyor, ExtTestCase


class TestNoteBooksBugLatex(ExtTestCase):

    def test_notebook_latex(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        path = os.path.abspath(os.path.split(__file__)[0])
        fold = os.path.normpath(os.path.join(path, "notebooks_latex"))
        nbs = [os.path.join(fold, _)
               for _ in os.listdir(fold) if ".ipynb" in _]
        formats = ["ipynb", "html", "python", "rst", "pdf"]

        temp = os.path.join(path, "temp_nb_bug_latex")
        if not os.path.exists(temp):
            os.mkdir(temp)
        for file in os.listdir(temp):
            os.remove(os.path.join(temp, file))

        if is_travis_or_appveyor() in ('travis', 'appveyor'):
            return

        res = process_notebooks(nbs, temp, temp, formats=formats)
        fLOG("*****", len(res))
        for _ in res:
            fLOG(_)
            self.assertExists(_[0])


if __name__ == "__main__":
    unittest.main()
