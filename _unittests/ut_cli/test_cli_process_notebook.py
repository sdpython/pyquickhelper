"""
@brief      test tree node (time=7s)
"""


import sys
import os
import unittest
from io import StringIO
import shutil
from pyquickhelper.loghelper import fLOG, BufferedPrint
from pyquickhelper.pycode import get_temp_folder, skipif_travis, skipif_appveyor
from pyquickhelper.__main__ import main


class TestProcessNotebook(unittest.TestCase):

    @skipif_travis("No latex installed.")
    @skipif_appveyor("No latex installed.")
    def test_process_notebook(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        temp = get_temp_folder(__file__, "temp_process_notebook")
        source = os.path.join(temp, "..", "data", "td1a_unit_test_ci.ipynb")

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

        st = BufferedPrint()
        main(args=["process_notebooks", "-n", source, "-o",
                   temp, "-b", temp, '-f', 'rst'], fLOG=st.fprint)
        res = str(st)
        self.assertIn("convert into  rst", res)


if __name__ == "__main__":
    unittest.main()
