"""
@brief      test log(time=1s)

notebook test
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
from src.pyquickhelper.ipythonhelper import find_notebook_kernel, install_jupyter_kernel, get_notebook_kernel, remove_kernel


class TestNotebookKernels(unittest.TestCase):

    def test_notebook_kernels_list(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        kern = "python" + str(sys.version_info[0])
        res = find_notebook_kernel()
        assert isinstance(res, dict)
        for k, v in sorted(res.items()):
            fLOG(k, type(v), v)
        assert kern in res

    def test_notebook_kernel_install(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        if "travis" in sys.executable:
            # permission issue on travis
            return

        kern = "ut_" + sys.executable.replace("\\", "/").replace("/", "_").replace(
            ".", "_").replace(":", "") + "_" + str(sys.version_info[0])
        kern = kern.lower()
        loc = install_jupyter_kernel(kernel_name=kern)
        fLOG("i", loc)
        if kern not in loc:
            raise Exception(
                "do not match '{0}' not in '{1}'".format(kern, loc))
        assert os.path.exists(loc)
        res = get_notebook_kernel(kern)
        fLOG("i", res)

        remove_kernel(kern)
        kernels = find_notebook_kernel()
        assert kern not in kernels

if __name__ == "__main__":
    unittest.main()
