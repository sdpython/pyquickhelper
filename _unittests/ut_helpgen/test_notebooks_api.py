"""
@brief      test log(time=7s)
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
from src.pyquickhelper.pycode import get_temp_folder
from src.pyquickhelper.helpgen import nb2slides, nb2html
from src.pyquickhelper.ipythonhelper import read_nb


class TestNotebookAPI (unittest.TestCase):

    def test_convert_slides_api(self):
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
        assert os.path.exists(nb)
        nbr = read_nb(nb)

        temp = get_temp_folder(__file__, "temp_nb_api")
        outfile = os.path.join(temp, "out_nb_slides.slides.html")
        res = nb2slides(nbr, outfile)
        assert len(res) > 1
        for r in res:
            assert os.path.exists(r)

        outfile = os.path.join(temp, "out_nb_slides.html")
        res = nb2html(nbr, outfile)
        assert len(res) == 1
        for r in res:
            assert os.path.exists(r)


if __name__ == "__main__":
    unittest.main()
