"""
@brief      test log(time=65s)
@author     Xavier Dupre
"""
import os
import unittest
import re
from pyquickhelper.loghelper import fLOG
from pyquickhelper.helpgen.sphinx_main import process_notebooks
from pyquickhelper.pycode import is_travis_or_appveyor, get_temp_folder, ExtTestCase


class TestNoteBooksBug(ExtTestCase):

    def test_regex(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        exp = re.compile(r"(.{3}[\\]\$)")
        s = ": [ ['$',"
        fLOG(s)
        r = exp.finditer(s)
        nb = 0
        for _ in r:
            fLOG("1", _.groups())
            nb += 1
        nb1 = nb

        s = r"\def\PYZdl{\char`\$}"
        fLOG(s)
        r = exp.finditer(s)
        nb = 0
        for _ in r:
            fLOG("2", _.groups())
            nb += 1

        self.assertEqual(nb1, 0)
        self.assertTrue(nb > 0)

    def test_notebook(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        path = os.path.abspath(os.path.split(__file__)[0])
        fold = os.path.normpath(os.path.join(path, "notebooks"))
        nbs = [os.path.join(fold, _)
               for _ in os.listdir(fold) if ".ipynb" in _]
        formats = ["ipynb", "python", "rst", "pdf"]

        temp = get_temp_folder(__file__, "temp_nb_bug")

        if is_travis_or_appveyor() in ('travis', 'appveyor'):
            return

        res = process_notebooks(nbs, temp, temp, formats=formats)
        fLOG("*****", len(res))
        for _ in res:
            if not os.path.exists(_[0]):
                raise Exception(_[0])

        check = os.path.join(temp, "td1a_correction_session4.tex")
        with open(check, "r", encoding="utf8") as f:
            content = f.read()
        if "\\section{" not in content:
            raise Exception(content)

    def test_notebook_html(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        path = os.path.abspath(os.path.split(__file__)[0])
        fold = os.path.normpath(os.path.join(path, "notebooks"))
        nbs = [os.path.join(fold, _)
               for _ in os.listdir(fold) if ".ipynb" in _]
        formats = ["html"]

        temp = get_temp_folder(__file__, "temp_nb_bug_html")

        if is_travis_or_appveyor() in ('travis', 'appveyor'):
            return

        res = process_notebooks(nbs, temp, temp, formats=formats)
        fLOG("*****", len(res))
        for _ in res:
            if not os.path.exists(_[0]):
                raise Exception(_[0])

    def test_notebook_slides(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        path = os.path.abspath(os.path.split(__file__)[0])
        fold = os.path.normpath(os.path.join(path, "notebooks"))
        nbs = [os.path.join(fold, _)
               for _ in os.listdir(fold) if ".ipynb" in _]
        formats = ["slides"]

        temp = get_temp_folder(__file__, "temp_nb_bug_slides")

        if is_travis_or_appveyor() in ('travis', 'appveyor'):
            return

        res = process_notebooks(nbs, temp, temp, formats=formats)
        fLOG("*****", len(res))
        for _ in res:
            if not os.path.exists(_[0]):
                raise Exception(_[0])

        checks = [os.path.join(temp, "reveal.js"),
                  os.path.join(temp, "require.js")]
        for check in checks:
            if not os.path.exists(check):
                raise Exception(check)

    def test_notebook_pdf(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
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

        if is_travis_or_appveyor() in ('travis', 'appveyor'):
            return

        res = process_notebooks(nbs, temp, temp, formats=formats)
        fLOG("*****", len(res))
        for _ in res:
            fLOG(_)
            self.assertExists(_[0])

        check = os.path.join(temp, "td1a_correction_session4.tex")
        with open(check, "r", encoding="utf8") as f:
            content = f.read()
        if "\\section{" not in content:
            raise Exception(content)


if __name__ == "__main__":
    unittest.main()
