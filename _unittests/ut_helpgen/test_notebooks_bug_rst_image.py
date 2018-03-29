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

from src.pyquickhelper.loghelper import fLOG, CustomLog
from src.pyquickhelper.helpgen import process_notebooks
from src.pyquickhelper.pycode import skipif_travis, skipif_appveyor, get_temp_folder, ExtTestCase


if sys.version_info[0] == 2:
    from codecs import open


class TestNoteBooksBugRstImage(ExtTestCase):

    @skipif_travis('latex')
    @skipif_appveyor('latex')
    def test_notebook_rst_image(self):
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
               for _ in os.listdir(fold) if ".ipynb" in _ and '_11' in _]
        formats = ["rst", ]

        temp = get_temp_folder(__file__, "temp_nb_bug_rst_image")

        res = process_notebooks(nbs, temp, temp, formats=formats, fLOG=fLOG)
        for _ in res:
            fLOG(_)
            self.assertExists(_[0])

        name = os.path.join(temp, "td1a_cenonce_session_11.rst")
        with open(name, "r", encoding="utf8") as f:
            content = f.read()
        exp = "output_7_0.png"
        if exp in content:
            raise Exception(content)
        exp = "td1a_cenonce_session_11_7_0.png"
        if exp not in content:
            raise Exception(content)


if __name__ == "__main__":
    unittest.main()
