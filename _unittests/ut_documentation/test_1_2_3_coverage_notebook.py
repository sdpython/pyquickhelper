#-*- coding: utf-8 -*-
"""
@brief      test log(time=21s)
"""

import sys
import os
import unittest


try:
    import src.pyquickhelper as thismodule
except ImportError:
    path = os.path.normpath(
        os.path.abspath(
            os.path.join(
                os.path.split(__file__)[0],
                "..",
                "..")))
    if path not in sys.path:
        sys.path.append(path)
    import src.pyquickhelper as thismodule

from src.pyquickhelper.loghelper import fLOG
from src.pyquickhelper.pycode import get_temp_folder
from src.pyquickhelper.ipythonhelper import execute_notebook_list, execute_notebook_list_finalize_ut, get_additional_paths
from src.pyquickhelper.filehelper import synchronize_folder
from src.pyquickhelper.pycode import add_missing_development_version


class TestNotebook123Coverage(unittest.TestCase):

    def setUp(self):
        add_missing_development_version(["jyquickhelper"],
                                        __file__, hide=True)

    def a_test_notebook_runner(self, name, folder, valid=None, copy_folder=None):
        temp = get_temp_folder(__file__, "temp_notebook_123_{0}".format(name))
        doc = os.path.join(temp, "..", "..", "..", "_doc", "notebooks", folder)
        self.assertTrue(os.path.exists(doc))
        keepnote = [os.path.join(doc, _) for _ in os.listdir(
            doc) if name in _ and os.path.splitext(_)[-1] == ".ipynb"]
        self.assertTrue(len(keepnote) > 0)

        if copy_folder is not None:
            if not os.path.exists(copy_folder):
                raise FileNotFoundError(copy_folder)
            dest = os.path.split(copy_folder)[-1]
            dest = os.path.join(temp, dest)
            if not os.path.exists(dest):
                os.mkdir(dest)
            synchronize_folder(copy_folder, dest, fLOG=fLOG)

        import jyquickhelper
        add_path = get_additional_paths([jyquickhelper, thismodule])
        res = execute_notebook_list(
            temp, keepnote, additional_path=add_path, valid=valid)
        execute_notebook_list_finalize_ut(res, fLOG=fLOG, dump=thismodule)

    def test_notebook_example_pyquickhelper(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        self.a_test_notebook_runner(
            "compare_python_distribution", "")


if __name__ == "__main__":
    unittest.main()
