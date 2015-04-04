"""
@brief      test log(time=2s)

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
from src.pyquickhelper.ipythonhelper import ipython_cython_extension



class TestCheckCython(unittest.TestCase):

    def test_ipython_cython_extension(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
            
        ipython_cython_extension()

if __name__ == "__main__":
    unittest.main()
