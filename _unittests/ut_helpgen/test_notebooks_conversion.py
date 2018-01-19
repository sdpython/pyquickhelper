"""
@brief      test log(time=8s)
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
from src.pyquickhelper.helpgen.sphinx_main import process_notebooks


if sys.version_info[0] == 2:
    from codecs import open


class TestNotebookConversion2(unittest.TestCase):

    def test_notebook_conversion_replacements(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        temp = get_temp_folder(
            __file__, "temp_notebook_conversion_replacements")
        this = os.path.join(temp, '..', "data", "TD_2A_Eco_Web_Scraping.ipynb")
        notebook_replacements = {'html': [('1ere page HTML', '2nd page-WWW')]}
        process_notebooks(this, build=temp, outfold=temp, formats=['html', 'slides'],
                          notebook_replacements=notebook_replacements)
        with open(os.path.join(temp, 'TD_2A_Eco_Web_Scraping.html'), 'r', encoding='utf-8') as f:
            text = f.read()
        self.assertNotIn(notebook_replacements['html'][0][0], text)
        self.assertIn(notebook_replacements['html'][0][1], text)
        with open(os.path.join(temp, 'TD_2A_Eco_Web_Scraping.slides.html'), 'r', encoding='utf-8') as f:
            text = f.read()
        self.assertIn(notebook_replacements['html'][0][0], text)
        self.assertNotIn(notebook_replacements['html'][0][1], text)


if __name__ == "__main__":
    unittest.main()
