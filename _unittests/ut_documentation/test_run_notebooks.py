#-*- coding: utf-8 -*-
"""
@brief      test log(time=33s)
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

try:
    import jyquickhelper as skip_
except ImportError:
    path = os.path.normpath(
        os.path.abspath(
            os.path.join(
                os.path.split(__file__)[0],
                "..",
                "..",
                "..",
                "jyquickhelper",
                "src")))
    if path not in sys.path:
        sys.path.append(path)
    import jyquickhelper as skip_

from src.pyquickhelper.loghelper import fLOG
from src.pyquickhelper.pycode import get_temp_folder
from src.pyquickhelper.ipythonhelper import execute_notebook_list, execute_notebook_list_finalize_ut
from src.pyquickhelper.pycode import is_travis_or_appveyor
from src.pyquickhelper.ipythonhelper import install_python_kernel_for_unittest


class TestRunNotebooks(unittest.TestCase):

    def test_run_notebook(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        if sys.version_info[0] == 2:
            # notebooks are not converted into python 2.7, so not tested
            return

        kernel_name = None if is_travis_or_appveyor() is not None else install_python_kernel_for_unittest(
            "pyquickhelper")

        temp = get_temp_folder(__file__, "temp_run_notebooks_pyq")

        fnb = os.path.normpath(os.path.join(
            os.path.abspath(os.path.dirname(__file__)), "..", "..", "_doc", "notebooks"))
        keepnote = []
        for f in os.listdir(fnb):
            if os.path.splitext(f)[-1] == ".ipynb":
                if "example_pyquickhelper" in f:
                    code_init = "form1={'version': 'modified', 'module': 'anything'}"
                    keepnote.append((os.path.join(fnb, f), code_init))
                elif "having_a_form" in f:
                    code_init = "myvar='my value'\nform1={'version': 'modified', 'module': 'anything'}"
                    code_init += "\ncredential={'password': 'hiddenpassword', 'login': 'admin'}"
                    code_init += "\nmy_address={'last_name': 'dupre', 'combined': 'xavier dupre', 'first_name': 'xavier'}"
                    keepnote.append((os.path.join(fnb, f), code_init))
                elif "javascript" in f:
                    # We skip due to connectivity issues.
                    pass
                elif "git_data" in f:
                    # Too long.
                    pass
                else:
                    keepnote.append(os.path.join(fnb, f))
        self.assertTrue(len(keepnote) > 0)

        def valid(cell):
            if "open_html_form" in cell:
                return False
            if "open_window_params" in cell:
                return False
            if '<div style="position:absolute' in cell:
                return False
            if "build_script.bat" in cell:
                return False
            return True

        import jyquickhelper
        addpaths = [os.path.normpath(os.path.join(
            os.path.abspath(os.path.dirname(__file__)), "..", "..", "src")),
            os.path.normpath(os.path.join(os.path.abspath(os.path.dirname(jyquickhelper.__file__)), ".."))]

        res = execute_notebook_list(
            temp, keepnote, fLOG=fLOG, valid=valid, additional_path=addpaths, kernel_name=kernel_name)
        execute_notebook_list_finalize_ut(
            res, fLOG=fLOG, dump=src.pyquickhelper)


if __name__ == "__main__":
    unittest.main()
