"""
@brief      test log(time=5s)
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
from src.pyquickhelper.pycode import get_temp_folder, is_travis_or_appveyor, ExtTestCase
from src.pyquickhelper.helpgen import nb2slides, nb2html, nb2rst
from src.pyquickhelper.ipythonhelper import read_nb


class TestNotebookAPI(ExtTestCase):

    def test_src_import(self):
        """for pylint"""
        self.assertTrue(src is not None)

    def test_convert_slides_api_html(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        if sys.version_info[0] == 2:
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

        temp = get_temp_folder(__file__, "temp_nb_api_html")
        outfile = os.path.join(temp, "out_nb_slides.slides.html")
        res = nb2slides(nbr, outfile)
        self.assertGreater(len(res), 1)
        for r in res:
            self.assertExists(r)

        outfile = os.path.join(temp, "out_nb_slides.html")
        res = nb2html(nbr, outfile)
        self.assertEqual(len(res), 1)
        for r in res:
            self.assertExists(r)

    def test_convert_slides_api_rst(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        if sys.version_info[0] == 2:
            return

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
        outfile = os.path.join(temp, "out_nb_slides.rst")
        res = nb2rst(nbr, outfile)
        self.assertEqual(len(res), 1)
        for r in res:
            self.assertExists(r)


if __name__ == "__main__":
    unittest.main()
