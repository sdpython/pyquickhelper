"""
@brief      test log(time=30s)
@author     Xavier Dupre
"""

import os
import unittest

from pyquickhelper.loghelper import fLOG
from pyquickhelper.helpgen.sphinx_main import process_notebooks
from pyquickhelper.helpgen.sphinx_main import setup_environment_for_help
from pyquickhelper.pycode import is_travis_or_appveyor, ExtTestCase


class TestNoteBooksBugPython(ExtTestCase):

    def test_notebook_python(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        path = os.path.abspath(os.path.split(__file__)[0])
        fold = os.path.normpath(os.path.join(path, "notebooks_python"))
        nbs = [os.path.join(fold, _)
               for _ in os.listdir(fold) if ".ipynb" in _]
        formats = ["python"]

        temp = os.path.join(path, "temp_nb_bug_python")
        if not os.path.exists(temp):
            os.mkdir(temp)
        for file in os.listdir(temp):
            os.remove(os.path.join(temp, file))

        if is_travis_or_appveyor() in ('travis', 'appveyor'):
            return

        setup_environment_for_help()

        res = process_notebooks(nbs, temp, temp, formats=formats)
        fLOG("*****", len(res))
        for _ in res:
            fLOG(_)
            self.assertExists(_[0])

        with open(os.path.join(temp, "seance5_approche_fonctionnelle_correction.py"), "r", encoding="utf8") as f:
            content = f.read()
        exp = "# -*- coding: utf-8 -*-"
        if exp not in content:
            raise AssertionError(content)


if __name__ == "__main__":
    unittest.main()
