"""
@brief      test log(time=65s)
@author     Xavier Dupre
"""

import sys
import os
import unittest
import re
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


class TestNoteBooksBug(unittest.TestCase):

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

        assert nb1 == 0
        assert nb > 0

    def test_notebook(self):
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
        formats = ["slides", "present", "ipynb", "html",
                   "python", "rst", "pdf", "docx"]

        temp = get_temp_folder(__file__, "temp_nb_bug")

        if is_travis_or_appveyor() is not None:
            warnings.warn(
                "travis, appveyor, unable to test TestNoteBooksBug.test_notebook")
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
        checks = [os.path.join(temp, "reveal.js"), os.path.join(temp, "require.js")]
        for check in checks:
            if not os.path.exists(check):
                raise Exception(check)

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

        if is_travis_or_appveyor() is not None:
            warnings.warn(
                "travis, appveyor, unable to test TestNoteBooksBug.test_notebook_pdf")
            return

        res = process_notebooks(nbs, temp, temp, formats=formats)
        fLOG("*****", len(res))
        for _ in res:
            fLOG(_)
            assert os.path.exists(_[0])

        check = os.path.join(temp, "td1a_correction_session4.tex")
        with open(check, "r", encoding="utf8") as f:
            content = f.read()
        if "\\section{" not in content:
            raise Exception(content)


if __name__ == "__main__":
    unittest.main()
