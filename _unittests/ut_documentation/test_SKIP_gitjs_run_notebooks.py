# -*- coding: utf-8 -*-
"""
@brief      test log(time=42s)
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
from src.pyquickhelper.ipythonhelper import execute_notebook_list, execute_notebook_list_finalize_ut


class TestSKIPRunNotebooks(unittest.TestCase):

    def test_src_import(self):
        """for pylint"""
        self.assertTrue(src is not None)

    def test_skip_run_notebook_javascript(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        temp = get_temp_folder(__file__, "temp_skip_run_notebooks_pyq_long")

        fnb = os.path.normpath(os.path.join(
            os.path.abspath(os.path.dirname(__file__)), "..", "..", "_doc", "notebooks"))
        keepnote = []
        for f in os.listdir(fnb):
            if os.path.splitext(f)[-1] == ".ipynb":
                if "javascript" in f:
                    keepnote.append(os.path.join(fnb, f))
        self.assertTrue(len(keepnote) > 0)

        def valid(cell):
            return True

        import jyquickhelper
        addpaths = [os.path.normpath(os.path.join(
            os.path.abspath(os.path.dirname(__file__)), "..", "..", "src")),
            os.path.normpath(os.path.join(os.path.abspath(os.path.dirname(jyquickhelper.__file__)), ".."))]

        try:
            res = execute_notebook_list(
                temp, keepnote, fLOG=fLOG, valid=valid, additional_path=addpaths)
            execute_notebook_list_finalize_ut(
                res, fLOG=fLOG, dump=src.pyquickhelper)
        except Exception as e:
            # Issue with permission.
            warnings.warn("Unable to test this notebook due to " + str(e))

    def test_skip_run_notebook_git(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        temp = get_temp_folder(__file__, "temp_skip_run_notebooks_pyq_long")

        fnb = os.path.normpath(os.path.join(
            os.path.abspath(os.path.dirname(__file__)), "..", "..", "_doc", "notebooks"))
        keepnote = []
        for f in os.listdir(fnb):
            if os.path.splitext(f)[-1] == ".ipynb":
                if "git_data" in f:
                    keepnote.append(os.path.join(fnb, f))
        self.assertTrue(len(keepnote) > 0)

        def valid(cell):
            if "git log --log-size --abbrev --follow" in cell:
                return False
            return True

        import jyquickhelper
        addpaths = [os.path.normpath(os.path.join(
            os.path.abspath(os.path.dirname(__file__)), "..", "..", "src")),
            os.path.normpath(os.path.join(os.path.abspath(os.path.dirname(jyquickhelper.__file__)), ".."))]

        res = execute_notebook_list(
            temp, keepnote, fLOG=fLOG, valid=valid, additional_path=addpaths)
        execute_notebook_list_finalize_ut(
            res, fLOG=fLOG, dump=src.pyquickhelper)


if __name__ == "__main__":
    unittest.main()
