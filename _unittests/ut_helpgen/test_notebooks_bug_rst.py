"""
@brief      test log(time=6s)
@author     Xavier Dupre
"""

import sys
import os
import unittest
import warnings

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
from src.pyquickhelper.pycode import is_travis_or_appveyor, get_temp_folder


if sys.version_info[0] == 2:
    from codecs import open


class TestNoteBooksBugRst(unittest.TestCase):

    def test_notebook_rst(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        if sys.version_info[0] == 2:
            # does not work on Python 2
            return
        path = os.path.abspath(os.path.split(__file__)[0])
        fold = os.path.normpath(os.path.join(path, "notebooks_rst"))
        nbs = [os.path.join(fold, _)
               for _ in os.listdir(fold) if ".ipynb" in _]
        formats = ["rst", ]

        temp = get_temp_folder(__file__, "temp_nb_bug_rst")
        clog = CustomLog(temp)
        clog("test_notebook_rst")

        if is_travis_or_appveyor() is not None:
            warnings.warn(
                "travis, appveyor, unable to test TestNoteBooksBugRst.test_notebook_rst")
            return

        clog("process_notebooks: begin")
        res = process_notebooks(nbs, temp, temp, formats=formats, fLOG=clog)
        clog("process_notebooks: end")
        fLOG("*****", len(res))
        for _ in res:
            fLOG(_)
            assert os.path.exists(_[0])

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
