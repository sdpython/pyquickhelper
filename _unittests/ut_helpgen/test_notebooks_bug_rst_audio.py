"""
@brief      test log(time=6s)
@author     Xavier Dupre
"""

import os
import unittest

from pyquickhelper.loghelper import fLOG, CustomLog
from pyquickhelper.helpgen.sphinx_main import process_notebooks
from pyquickhelper.pycode import skipif_travis, skipif_appveyor, get_temp_folder, ExtTestCase


class TestNoteBooksBugRstAudio(ExtTestCase):

    @skipif_travis('latex')
    @skipif_appveyor('latex')
    def test_notebook_rst_ausdio(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        formats = ["rst", ]
        temp = get_temp_folder(__file__, "temp_nb_bug_rst_audio")
        nbs = [os.path.join(temp, '..', 'data', 'exemple_div.ipynb')]
        clog = CustomLog(temp)
        clog("test_notebook_rst_audio")

        fold = 'static'
        if not os.path.exists(fold):
            os.mkdir(fold)
        sty = os.path.join(fold, 'rst.tpl')
        if not os.path.exists(sty):
            sr = os.path.join(temp, '..', 'data', 'rst.tpl')
            if not os.path.exists(sr):
                raise FileNotFoundError(sr)
            shutil.copy(sr, fold)

        clog("process_notebooks: begin")
        process_notebooks(nbs, temp, temp, formats=formats, fLOG=clog)
        clog("process_notebooks: end")

        name = os.path.join(temp, "exemple_div.rst")
        clog("final checking", name)
        with open(name, "r", encoding="utf8") as f:
            content = f.read()
        clog("final read", name)
        exp = ".. raw:: html"
        if exp not in content:
            raise Exception(content)
        clog("done")


if __name__ == "__main__":
    unittest.main()
