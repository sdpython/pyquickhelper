"""
@brief      test log(time=36s)
@author     Xavier Dupre
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

from src.pyquickhelper.loghelper import fLOG
from src.pyquickhelper.helpgen import process_notebooks
from src.pyquickhelper.pycode import get_temp_folder, skipif_travis, skipif_appveyor


if sys.version_info[0] == 2:
    from codecs import open


class TestNoteBooksBugJs(unittest.TestCase):

    @skipif_travis('latex, pandoc not installed')
    @skipif_appveyor('latex, pandoc not installed')
    def test_notebook_js(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        if sys.version_info[0] == 2:
            # does not work on Python 2
            return
        path = os.path.abspath(os.path.split(__file__)[0])
        fold = os.path.normpath(os.path.join(path, "notebooks_js"))
        nbs = [os.path.join(fold, _)
               for _ in os.listdir(fold) if ".ipynb" in _]
        formats = ["slides", "present", "ipynb", "html",
                   "python", "rst", "pdf"]
        if sys.platform.startswith("win"):
            formats.append("docx")

        temp = get_temp_folder(__file__, "temp_nb_bug_js")

        res = process_notebooks(nbs, temp, temp, formats=formats)
        fLOG("*****", len(res))
        for _ in res:
            if not os.path.exists(_[0]):
                raise Exception(_[0])

        check = os.path.join(temp, "using_qgrid_with_jsdf.tex")
        with open(check, "r", encoding="utf8") as f:
            content = f.read()
        if "\\section{" not in content:
            raise Exception(content)
        checks = [os.path.join(temp, "reveal.js"),
                  os.path.join(temp, "require.js")]
        for check in checks:
            if not os.path.exists(check):
                raise Exception(check)

    @skipif_travis('latex, pandoc not installed')
    @skipif_appveyor('latex, pandoc not installed')
    def test_notebook_pdf(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        if sys.version_info[0] == 2:
            # does not work on Python 2
            return
        path = os.path.abspath(os.path.split(__file__)[0])
        fold = os.path.normpath(os.path.join(path, "notebooks"))
        nbs = [os.path.join(fold, _)
               for _ in os.listdir(fold) if ".ipynb" in _]
        formats = ["latex", "pdf"]

        temp = os.path.join(path, "temp_nb_bug_pdf")
        if not os.path.exists(temp):
            os.mkdir(temp)
        for file in os.listdir(temp):
            os.remove(os.path.join(temp, file))

        res = process_notebooks(nbs, temp, temp, formats=formats)
        fLOG("*****", len(res))
        for _ in res:
            fLOG(_)
            self.assertTrue(os.path.exists(_[0]))

        check = os.path.join(temp, "td1a_correction_session4.tex")
        with open(check, "r", encoding="utf8") as f:
            content = f.read()
        if "\\section{" not in content:
            raise Exception(content)


if __name__ == "__main__":
    unittest.main()
