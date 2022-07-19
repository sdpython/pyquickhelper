"""
@brief      test log(time=5s)
@author     Xavier Dupre
"""

import sys
import os
import unittest
import shutil

from pyquickhelper.loghelper import fLOG
from pyquickhelper.pycode import get_temp_folder, is_travis_or_appveyor, ExtTestCase
from pyquickhelper.helpgen import nb2slides, nb2html, nb2rst
from pyquickhelper.ipythonhelper import read_nb


class TestNotebookAPI(ExtTestCase):

    def test_convert_slides_api_html(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        path = os.path.abspath(os.path.split(__file__)[0])
        fold = os.path.normpath(
            os.path.join(
                path,
                "..",
                "..",
                "_doc",
                "notebooks"))
        nb = os.path.join(fold, "example_pyquickhelper.ipynb")
        self.assertExists(nb)
        nbr = read_nb(nb, kernel=False)

        temp = get_temp_folder(__file__, "temp_nb_api_html")
        outfile = os.path.join(temp, "out_nb_slides.slides.html")
        res = nb2slides(nbr, outfile)
        self.assertGreater(len(res), 1)
        for r in res:
            self.assertExists(r)

        outfile = os.path.join(temp, "out_nb_slides.html")
        fold = 'static'
        if not os.path.exists(fold):
            os.mkdir(fold)
        sty = os.path.join(fold, 'style.css')
        if not os.path.exists(sty):
            sr = os.path.join(temp, '..', 'data', 'style.css')
            if not os.path.exists(sr):
                raise FileNotFoundError(sr)
            shutil.copy(sr, fold)

        res = nb2html(nbr, outfile)
        self.assertEqual(len(res), 1)
        for r in res:
            self.assertExists(r)

    def test_convert_slides_api_rst(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        if is_travis_or_appveyor() in ('travis', 'appveyor'):
            # no latex, no pandoc
            return

        path = os.path.abspath(os.path.split(__file__)[0])
        fold = os.path.normpath(
            os.path.join(
                path,
                "..",
                "..",
                "_doc",
                "notebooks"))
        nb = os.path.join(fold, "example_pyquickhelper.ipynb")
        self.assertExists(nb)
        nbr = read_nb(nb, kernel=False)

        temp = get_temp_folder(__file__, "temp_nb_api_rst")
        outfile = os.path.join(temp, "out_nb_slides.html")
        fold = 'static'
        if not os.path.exists(fold):
            os.mkdir(fold)
        for tpl in ['rst', 'display_priority', 'null']:
            sty = os.path.join(fold, f'{tpl}.tpl')
            sr = os.path.join(temp, '..', 'data', f'{tpl}.tpl')
            if not os.path.exists(sr):
                raise FileNotFoundError(sr)
            if not os.path.exists(sty):
                shutil.copy(sr, fold)
            if not os.path.exists(f'{tpl}.tpl'):
                shutil.copy(sr, '.')

        outfile = os.path.join(temp, "out_nb_slides.rst")
        res = nb2rst(nbr, outfile)
        self.assertEqual(len(res), 1)
        for r in res:
            self.assertExists(r)


if __name__ == "__main__":
    unittest.main()
