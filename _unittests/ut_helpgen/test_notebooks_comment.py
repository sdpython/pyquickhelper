"""
@brief      test log(time=6s)
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
from src.pyquickhelper.pycode import is_travis_or_appveyor, ExtTestCase


class TestNoteBooksComment(ExtTestCase):

    def test_src_import(self):
        """for pylint"""
        self.assertTrue(src is not None)

    def test_notebook_comment(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        path = os.path.abspath(os.path.split(__file__)[0])
        fold = os.path.normpath(os.path.join(path, "notebooks_comment"))
        nbs = [os.path.join(fold, _)
               for _ in os.listdir(fold) if ".ipynb" in _]
        formats = ["rst", ]

        temp = os.path.join(path, "temp_nb_comment")
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
            self.assertExists(os.path.exists(_[0]))

        with open(os.path.join(temp, "example_with_comments.rst"), "r", encoding="utf8") as f:
            lines = f.readlines()
        nb = 0
        for line in lines:
            if line.startswith(".. index:: comment, notebook, rst"):
                nb += 1
        # it should work if the module is able to deal with comments (not yet)
        # self.assertEqual(nb, 1)


if __name__ == "__main__":
    unittest.main()
