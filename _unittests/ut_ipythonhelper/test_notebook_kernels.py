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
from src.pyquickhelper.ipythonhelper import find_notebook_kernel


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

if __name__ == "__main__":
    unittest.main()
