"""
@brief      test log(time=12s)
@author     Xavier Dupre
"""

import sys
import os
import unittest
import shutil
from pyquickhelper.loghelper import fLOG
from pyquickhelper.pycode import get_temp_folder, ExtTestCase, skipif_appveyor
from pyquickhelper.helpgen.sphinx_main import process_notebooks


class TestNotebookConversion2(ExtTestCase):

    @skipif_appveyor("missing miktex")
    def test_notebook_conversion_replacements(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        temp = get_temp_folder(
            __file__, "temp_notebook_conversion_replacements")

        fold = 'static'
        if not os.path.exists(fold):
            os.mkdir(fold)
        for tpl in ['rst', 'display_priority', 'null']:
            sty = os.path.join(fold, '%s.tpl' % tpl)
            sr = os.path.join(temp, '..', 'data', '%s.tpl' % tpl)
            if not os.path.exists(sr):
                raise FileNotFoundError(sr)
            if not os.path.exists(sty):
                shutil.copy(sr, fold)
            if not os.path.exists('%s.tpl' % tpl):
                shutil.copy(sr, '.')

        this = os.path.join(temp, '..', "data", "TD_2A_Eco_Web_Scraping.ipynb")
        notebook_replacements = {'html': [('1ere page HTML', '2nd page-WWW')]}
        process_notebooks(this, build=temp, outfold=temp, formats=['html', 'slides'],
                          notebook_replacements=notebook_replacements)
        with open(os.path.join(temp, 'TD_2A_Eco_Web_Scraping2html.html'), 'r', encoding='utf-8') as f:
            text = f.read()
        self.assertNotIn(notebook_replacements['html'][0][0], text)
        self.assertIn(notebook_replacements['html'][0][1], text)
        with open(os.path.join(temp, 'TD_2A_Eco_Web_Scraping.slides.html'), 'r', encoding='utf-8') as f:
            text = f.read()
        self.assertIn(notebook_replacements['html'][0][0], text)
        self.assertNotIn(notebook_replacements['html'][0][1], text)


if __name__ == "__main__":
    unittest.main()
