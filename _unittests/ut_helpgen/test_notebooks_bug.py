"""
@brief      test log(time=65s)
@author     Xavier Dupre
"""
import os
import unittest
import re
from pyquickhelper.helpgen.sphinx_main import process_notebooks
from pyquickhelper.pycode import is_travis_or_appveyor, get_temp_folder, ExtTestCase


class TestNoteBooksBug(ExtTestCase):

    def test_regex(self):
        exp = re.compile(r"(.{3}[\\]\$)")
        s = ": [ ['$',"
        r = exp.finditer(s)
        nb = 0
        for _ in r:
            nb += 1
        nb1 = nb

        s = r"\def\PYZdl{\char`\$}"
        r = exp.finditer(s)
        nb = 0
        for _ in r:
            nb += 1

        self.assertEqual(nb1, 0)
        self.assertTrue(nb > 0)

    def test_notebook_html(self):
        path = os.path.abspath(os.path.split(__file__)[0])
        fold = os.path.normpath(os.path.join(path, "notebooks"))
        nbs = [os.path.join(fold, _)
               for _ in os.listdir(fold) if ".ipynb" in _]
        formats = ["html"]

        temp = get_temp_folder(__file__, "temp_nb_bug_html")

        if is_travis_or_appveyor() in ('travis', 'appveyor'):
            return

        res = process_notebooks(nbs, temp, temp, formats=formats)
        for _ in res:
            if not os.path.exists(_[0]):
                raise Exception(_[0])

    def test_notebook_slides(self):
        path = os.path.abspath(os.path.split(__file__)[0])
        fold = os.path.normpath(os.path.join(path, "notebooks"))
        nbs = [os.path.join(fold, _)
               for _ in os.listdir(fold) if ".ipynb" in _]
        formats = ["slides"]

        temp = get_temp_folder(__file__, "temp_nb_bug_slides")

        if is_travis_or_appveyor() in ('travis', 'appveyor'):
            return

        res = process_notebooks(nbs, temp, temp, formats=formats)
        for _ in res:
            if not os.path.exists(_[0]):
                raise Exception(_[0])

        checks = [os.path.join(temp, "reveal.js"),
                  os.path.join(temp, "require.js")]
        for check in checks:
            if not os.path.exists(check):
                raise Exception(check)


if __name__ == "__main__":
    unittest.main(verbosity=2)
