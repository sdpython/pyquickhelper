"""
@brief      test log(time=65s)
@author     Xavier Dupre
"""

import sys
import os
import unittest
import warnings


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

from src.pyquickhelper.loghelper import fLOG
from src.pyquickhelper.helpgen import process_notebooks
from src.pyquickhelper.pycode import is_travis_or_appveyor, get_temp_folder


if sys.version_info[0] == 2:
    from codecs import open


class TestNoteBooksBugRaw(unittest.TestCase):

    def test_notebook_raw(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        path = os.path.abspath(os.path.split(__file__)[0])
        fold = os.path.normpath(os.path.join(path, "data"))
        nbs = [os.path.join(fold, _)
               for _ in os.listdir(fold) if "TD_2A" in _]
        assert len(nbs) > 0
        formats = ["latex", "present", "ipynb", "html",
                   "python", "rst", "pdf", "docx"][:1]

        temp = get_temp_folder(__file__, "temp_nb_bug_raw")

        if is_travis_or_appveyor() is not None:
            warnings.warn(
                "travis, appveyor, unable to test TestNoteBooksBug.test_notebook")
            return

        res = process_notebooks(nbs, temp, temp, formats=formats)
        fLOG("*****", len(res))
        for _ in res:
            fLOG(_)
            assert os.path.exists(_[0])

        check = os.path.join(temp, "TD_2A_Eco_Web_Scraping.tex")
        with open(check, "r", encoding="utf8") as f:
            content = f.read()
        if "\\begin{verbatim" not in content:
            raise Exception(content)


if __name__ == "__main__":
    unittest.main()
