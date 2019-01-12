"""
@brief      test log(time=19s)
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
from src.pyquickhelper.pycode import is_travis_or_appveyor, get_temp_folder, ExtTestCase


class TestNoteBooksBugPdfIndicatrice(ExtTestCase):

    def test_src_import(self):
        """for pylint"""
        self.assertTrue(src is not None)

    def test_notebook_pdfa_indicatrice(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        if is_travis_or_appveyor() in ('travis', 'appveyor'):
            return
        path = os.path.abspath(os.path.split(__file__)[0])
        fold = os.path.normpath(os.path.join(path, "data"))
        nbs = [os.path.join(fold, "classification_multiple.ipynb")]
        formats = ["pdf"]

        temp = get_temp_folder(__file__, 'temp_nb_bug_pdfa_indicatrice')

        res = process_notebooks(nbs, temp, temp, formats=formats)
        fLOG("*****", len(res))
        for _ in res:
            fLOG(_)
            self.assertExists(_[0])
        lat = os.path.join(temp, 'classification_multiple.tex')
        with open(lat, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertNotIn('\\mathbf{1}', content)
        self.assertNotIn('probl?me', content)


if __name__ == "__main__":
    unittest.main()
