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
from src.pyquickhelper.helpgen.post_process import update_notebook_link


if sys.version_info[0] == 2:
    from codecs import open


class TestNoteBooksFind(ExtTestCase):

    def test_update_link_rst(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        text = "a link `ahah <find://rstref>`_ hello"
        link = update_notebook_link(text, "rst", None, fLOG)
        self.assertEqual(link, "a link :ref:`ahah <rstref>` hello")

    def test_update_link_html(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        text = "a link <a href=\"find://rstref\">ahah</a> hello"
        link = update_notebook_link(text, "html", None, fLOG)
        self.assertEqual(link, 'a link <a href="rstref.html">ahah</a> hello')

    def test_update_link_python(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        text = "a link [find://rstref](ahah) hello"
        link = update_notebook_link(text, "python", None, fLOG)
        self.assertEqual(link, 'a link [find://rstref](ahah) hello')
        link = update_notebook_link(text, "ipynb", None, fLOG)
        self.assertEqual(link, 'a link [find://rstref](ahah) hello')

    def test_update_link_latex(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        text = "a link \\href{find://reftag}{internal\\_link} hello"
        link = update_notebook_link(text, "latex", None, fLOG)
        self.assertEqual(
            link, 'a link \\href{reftag.html}{internal\\_link} hello')

        text = "notebook \\href{find://slideshowrst}{a link}"
        link = update_notebook_link(
            text, "latex", {'slideshowrst': 'http://sl.html'}, fLOG)
        self.assertEqual(
            link, 'notebook \\href{http://sl.html}{a link}')

    def test_notebook_find(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        if sys.version_info[0] == 2:
            # does not work on Python 2
            return
        path = os.path.abspath(os.path.split(__file__)[0])
        fold = os.path.normpath(os.path.join(path, "notebooks_find"))
        nbs = [os.path.join(fold, _)
               for _ in os.listdir(fold) if ".ipynb" in _]
        formats = ["slides", "rst", "present", "ipynb", "html",
                   "python", "pdf"]
        if sys.platform.startswith("win"):
            formats.append("docx")

        temp = get_temp_folder(__file__, "temp_nb_find")

        if is_travis_or_appveyor() in ('travis', 'appveyor'):
            return

        nbs2 = []
        for r in nbs:
            r2 = os.path.join(temp, os.path.split(r)[-1])
            shutil.copy(r, r2)
            nbs2.append(r2)
            r = upgrade_notebook(r2)
            fLOG("change", r)
        nblinks = {('reftag', 'ipynb'): 'http://something',
                   ('reftag', 'python'): 'http://something'}
        res = process_notebooks(
            nbs2, temp, temp, formats=formats, exc=False, nblinks=nblinks)
        fLOG("*****", len(res))
        for _ in res:
            fLOG(_)
            self.assertTrue(os.path.exists(_[0]))

        check = os.path.join(temp, "nb_find.tex")
        with open(check, "r", encoding="utf8") as f:
            content = f.read()
        self.assertTrue("\\end{document}" in content)


if __name__ == "__main__":
    unittest.main()
