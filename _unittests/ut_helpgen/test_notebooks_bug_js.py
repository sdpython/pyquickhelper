"""
@brief      test log(time=36s)
@author     Xavier Dupre
"""
import sys
import os
import unittest
from pyquickhelper.helpgen.sphinx_main import process_notebooks
from pyquickhelper.pycode import get_temp_folder, skipif_travis, skipif_appveyor, ExtTestCase


class TestNoteBooksBugJs(ExtTestCase):

    @skipif_travis('latex, pandoc not installed')
    @skipif_appveyor('latex, pandoc not installed')
    def test_notebook_js(self):
        path = os.path.abspath(os.path.split(__file__)[0])
        fold = os.path.normpath(os.path.join(path, "notebooks_js"))
        nbs = [os.path.join(fold, _)
               for _ in os.listdir(fold) if ".ipynb" in _]
        formats = ["slides", "ipynb", "html",
                   "python", "rst", "pdf"]
        if sys.platform.startswith("win"):
            formats.append("docx")

        temp = get_temp_folder(__file__, "temp_nb_bug_js")

        res = process_notebooks(nbs, temp, temp, formats=formats)
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


if __name__ == "__main__":
    unittest.main()
