"""
@brief      test log(time=6s)
@author     Xavier Dupre
"""

import os
import unittest
from pyquickhelper.helpgen.sphinx_main import process_notebooks
from pyquickhelper.pycode import skipif_travis, skipif_appveyor, get_temp_folder, ExtTestCase


class TestNoteBooksBugRstImage(ExtTestCase):

    @skipif_travis('latex')
    @skipif_appveyor('latex')
    def test_notebook_rst_image_3a(self):
        path = os.path.abspath(os.path.split(__file__)[0])
        fold = os.path.normpath(os.path.join(path, "notebooks"))
        nbs = [os.path.join(fold, _)
               for _ in os.listdir(fold) if ".ipynb" in _ and '3A' in _]
        formats = ["rst", ]

        temp = get_temp_folder(__file__, "temp_nb_bug_rst_image_3A")

        res = process_notebooks(nbs, temp, temp, formats=formats)
        for _ in res:
            self.assertExists(_[0])

        name = os.path.join(temp, "td2a_cenonce_session_3A.rst")
        with open(name, "r", encoding="utf8") as f:
            content = f.read()
        exp = "output_7_0.png"
        if exp in content:
            raise AssertionError(content)
        exp = "td2a_cenonce_session_3A_12_0.png"
        if exp not in content:
            raise AssertionError(content)


if __name__ == "__main__":
    unittest.main()
