"""
@brief      test log(time=65s)
@author     Xavier Dupre
"""

import sys
import os
import unittest
import shutil

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
from src.pyquickhelper.pycode import is_travis_or_appveyor, get_temp_folder, ExtTestCase
from src.pyquickhelper.ipythonhelper import upgrade_notebook


if sys.version_info[0] == 2:
    from codecs import open


class TestNoteBooksBug2(ExtTestCase):

    def test_notebook(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        if sys.version_info[0] == 2:
            # does not work on Python 2
            return
        path = os.path.abspath(os.path.split(__file__)[0])
        fold = os.path.normpath(os.path.join(path, "notebooks2"))
        nbs = [os.path.join(fold, _)
               for _ in os.listdir(fold) if ".ipynb" in _]
        formats = ["present", "ipynb", "html",
                   "python", "rst", "pdf"]
        if sys.platform.startswith("win"):
            formats.append("docx")

        temp = get_temp_folder(__file__, "temp_nb_bug2")

        if is_travis_or_appveyor() in ('travis', 'appveyor'):
            return

        nbs2 = []
        for r in nbs:
            r2 = os.path.join(temp, os.path.split(r)[-1])
            shutil.copy(r, r2)
            nbs2.append(r2)
            r = upgrade_notebook(r2)
            fLOG("change", r)
        res = process_notebooks(nbs2, temp, temp, formats=formats, exc=False)
        fLOG("*****", len(res))
        for _ in res:
            fLOG(_)
            self.assertExists(os.path.exists(_[0]))

        check = os.path.join(temp, "miparcours.tex")
        with open(check, "r", encoding="utf8") as f:
            content = f.read()
        self.assertIn("\\end{document}", content)


if __name__ == "__main__":
    unittest.main()
