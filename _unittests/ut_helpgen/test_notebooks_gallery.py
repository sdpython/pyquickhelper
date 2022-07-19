"""
@brief      test log(time=15s)
@author     Xavier Dupre
"""

import sys
import os
import unittest

from pyquickhelper.loghelper import fLOG
from pyquickhelper.helpgen.sphinx_main import build_notebooks_gallery
from pyquickhelper.pycode import get_temp_folder, ExtTestCase


class TestNotebookGallery(ExtTestCase):

    def a_test_notebook_gallery(self, layout):
        temp = get_temp_folder(__file__, f"temp_gallery_{layout}")
        fold = os.path.normpath(os.path.join(
            temp, "..", "data_gallery", "notebooks"))
        self.assertTrue(os.path.exists(fold))

        file = os.path.join(temp, "all_notebooks.rst")
        build_notebooks_gallery(fold, file, fLOG=fLOG, layout=layout)
        if not os.path.exists(file):
            raise FileNotFoundError(file)

        with open(file, "r", encoding="utf8") as f:
            text = f.read()

        if "GitHub/pyquickhelper" in text.replace("\\", "/"):
            raise Exception(text)
        if "Compter les occurences de nombres dans une liste" not in text:
            raise Exception(text)
        return text

    def test_notebook_gallery_classic(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        text = self.a_test_notebook_gallery('classic')
        self.assertIn(".. toctree::", text)
        spl = text.split(":hidden:")
        if len(spl) > 2:
            raise Exception(text)
        spl = text.split("notebooks/td2a_eco_competition_modeles_logistiques")
        if len(spl) != 3:
            raise Exception(text)

    def test_notebook_gallery_table(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        text = self.a_test_notebook_gallery('table')
        if ":hidden:" not in text:
            raise Exception(text)
        if ".. raw:: html" in text:
            raise Exception(text)
        spl = text.split("notebooks/td2a_eco_competition_modeles_logistiques")
        if len(spl) != 4:
            raise Exception(text)


if __name__ == "__main__":
    unittest.main()
