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


class TestNoteBooksBugRst(ExtTestCase):

    def test_src_import(self):
        """for pylint"""
        self.assertTrue(src is not None)

    @skipif_travis('latex')
    @skipif_appveyor('latex')
    def test_notebook_rst(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        path = os.path.abspath(os.path.split(__file__)[0])
        fold = os.path.normpath(os.path.join(path, "notebooks_rst"))
        nbs = [os.path.join(fold, _)
               for _ in os.listdir(fold) if ".ipynb" in _]
        formats = ["rst", ]

        temp = get_temp_folder(__file__, "temp_nb_bug_rst")
        clog = CustomLog(temp)
        clog("test_notebook_rst")

        clog("process_notebooks: begin")
        res = process_notebooks(nbs, temp, temp, formats=formats, fLOG=clog)
        clog("process_notebooks: end")
        fLOG("*****", len(res))
        for _ in res:
            fLOG(_)
            self.assertExists(_[0])

        name = os.path.join(temp, "having_a_form_in_a_notebook.rst")
        clog("final checking", name)
        with open(name, "r", encoding="utf8") as f:
            content = f.read()
        clog("final read", name)
        exp = "<#Animated-output>`"
        if exp in content or exp.lower() not in content:
            raise Exception(content)
        clog("done")


if __name__ == "__main__":
    unittest.main()
