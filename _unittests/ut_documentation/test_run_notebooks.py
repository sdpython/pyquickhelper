#-*- coding: utf-8 -*-
"""
@brief      test log(time=33s)
"""

import sys
import os
import unittest
import re

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


from src.pyquickhelper import fLOG, get_temp_folder
from src.pyquickhelper.ipythonhelper import execute_notebook_list
from src.pyquickhelper.pycode import compare_module_version
import IPython


class TestRunNotebooks(unittest.TestCase):

    def test_run_notebook(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        if sys.version_info[0] == 2:
            # notebooks are not converted into python 2.7, so not tested
            return

        if compare_module_version(IPython.__version__, "4.0.0") < 0:
            # IPython is not recnt enough
            return

        temp = get_temp_folder(__file__, "temp_run_notebooks")

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
                else:
                    keepnote.append(os.path.join(fnb, f))
        assert len(keepnote) > 0

        def valid(cell):
            if "open_html_form" in cell:
                return False
            if "open_window_params" in cell:
                return False
            if '<div style="position:absolute' in cell:
                return False
            return True

        addpaths = [os.path.normpath(os.path.join(
            os.path.abspath(os.path.dirname(__file__)), "..", "..", "src"))]
        res = execute_notebook_list(
            temp, keepnote, fLOG=fLOG, valid=valid, additional_path=addpaths)
        assert len(res) > 0
        fails = [(os.path.split(k)[-1], v)
                 for k, v in sorted(res.items()) if not v[0]]
        for f in fails:
            fLOG(f)
        for k, v in sorted(res.items()):
            name = os.path.split(k)[-1]
            fLOG(name, v[0], v[1])
        if len(fails) > 0:
            raise fails[0][1][-1]

if __name__ == "__main__":
    unittest.main()
