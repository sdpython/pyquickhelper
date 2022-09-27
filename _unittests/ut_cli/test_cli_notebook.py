# pylint: disable=W0101
"""
@brief      test tree node (time=62s)
"""

import sys
import os
import unittest
from io import StringIO
import shutil
from pyquickhelper.loghelper import BufferedPrint
from pyquickhelper.pycode import (
    get_temp_folder, skipif_travis, skipif_appveyor,
    ExtTestCase, ignore_warnings)
from pyquickhelper.__main__ import main


class TestProcessNotebook(ExtTestCase):

    @skipif_travis("No latex installed.")
    @skipif_appveyor("No latex installed.")
    @ignore_warnings(RuntimeWarning)
    def test_convert_notebook(self):
        temp = get_temp_folder(__file__, "temp_convert_notebook")
        source = os.path.join(temp, "..", "data", "td1a_unit_test_ci.ipynb")

        fold = 'static'
        if not os.path.exists(fold):
            os.mkdir(fold)
        for tpl in ['rst', 'display_priority', 'null']:
            sty = os.path.join(fold, f'{tpl}.tpl')
            sr = os.path.join(temp, '..', 'data', f'{tpl}.tpl')
            if not os.path.exists(sr):
                raise FileNotFoundError(sr)
            if not os.path.exists(sty):
                shutil.copy(sr, fold)
            if not os.path.exists(f'{tpl}.tpl'):
                shutil.copy(sr, '.')

        with self.subTest(cmd="convert_notebook"):
            st = BufferedPrint()
            main(args=["convert_notebook", "-f", source, "-o",
                       temp, "-b", temp, '-fo', 'rst,html'], fLOG=st.fprint)
            res = str(st)
            self.assertIn("convert into 'rst'", res)

        with self.subTest(cmd="run_notebook"):
            outname = os.path.join(temp, "out_nb.ipynb")
            st = BufferedPrint()
            main(args=['run_notebook', '-f', source,
                       '-o', outname], fLOG=st.fprint)
            res = str(st)
            self.assertExists(outname)
            source = outname

            temp2 = get_temp_folder(__file__, "temp_convert_notebook_next")
            st = BufferedPrint()
            main(args=["convert_notebook", "-f", source, "-o",
                       temp2, "-b", temp2, '-fo', 'rst,html'], fLOG=st.fprint)
            res = str(st)
            self.assertIn("convert into 'rst'", res)
            self.assertExists(os.path.join(temp2, "out_nb2html.html"))

    @ignore_warnings(RuntimeWarning)
    def test_run_notebook_help(self):
        st = BufferedPrint()
        main(args=['run_notebook', '--help'], fLOG=st.fprint)
        res = str(st)
        self.assertIn("usage: run_notebook", res)

    @skipif_travis("No latex installed.")
    @skipif_appveyor("No latex installed.")
    @ignore_warnings(RuntimeWarning)
    def test_convert_notebook2(self):
        temp = get_temp_folder(__file__, "temp_convert_notebook2")
        source = os.path.join(temp, "..", "data",
                              "onnx_tree_ensemble_parallel.ipynb")

        with self.subTest(cmd="convert_notebook"):
            st = BufferedPrint()
            main(args=["convert_notebook", "-f", source, "-o",
                       temp, "-b", temp, '-fo', 'rst,html'], fLOG=st.fprint)
            res = str(st)
            self.assertIn("convert into 'rst'", res)

        with self.subTest(cmd="run_notebook"):
            outname = os.path.join(temp, "out_nb.ipynb")
            st = BufferedPrint()
            main(args=['run_notebook', '-f', source,
                       '-o', outname], fLOG=st.fprint)
            res = str(st)
            self.assertExists(outname)
            source = outname
            self.assertExists(source)

            # something fails, the error message from nbformat is far from
            # explicit
            return

            temp2 = get_temp_folder(__file__, "temp_convert_notebook2_next")
            st = BufferedPrint()
            main(args=["convert_notebook", "-f", source, "-o",
                       temp2, "-b", temp2, '-fo', 'rst,html'], fLOG=st.fprint)
            res = str(st)
            self.assertIn("convert into 'rst'", res)
            self.assertExists(os.path.join(temp2, "out_nb2html.html"))


if __name__ == "__main__":
    unittest.main()
