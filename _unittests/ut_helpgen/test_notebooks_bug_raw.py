"""
@brief      test log(time=65s)
@author     Xavier Dupre
"""
import sys
import os
import unittest

from pyquickhelper.loghelper import fLOG
from pyquickhelper.helpgen.sphinx_main import process_notebooks
from pyquickhelper.pycode import is_travis_or_appveyor, get_temp_folder, ExtTestCase


class TestNoteBooksBugRaw(ExtTestCase):

    def test_notebook_raw(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        path = os.path.abspath(os.path.split(__file__)[0])
        fold = os.path.normpath(os.path.join(path, "data"))
        nbs = [os.path.join(fold, _)
               for _ in os.listdir(fold) if "TD_2A" in _]
        self.assertGreater(len(nbs), 0)
        formats = ["latex", "ipynb", "html",
                   "python", "rst", "pdf"]
        if sys.platform.startswith("win"):
            formats.append("docx")

        temp = get_temp_folder(__file__, "temp_nb_bug_raw")

        if is_travis_or_appveyor() in ('travis', 'appveyor'):
            return

        res = process_notebooks(nbs, temp, temp, formats=formats)
        fLOG("*****", len(res))
        for _ in res:
            fLOG(_)
            self.assertExists(_[0])

        check = os.path.join(temp, "TD_2A_Eco_Web_Scraping.tex")
        with open(check, "r", encoding="utf8") as f:
            content = f.read()
        if "\\begin{verbatim" not in content:
            raise Exception(content)


if __name__ == "__main__":
    unittest.main()
