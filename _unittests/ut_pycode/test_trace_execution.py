"""
@brief      test tree node (time=5s)
"""


import sys
import os
import unittest
import re
import shutil
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

from src.pyquickhelper import fLOG, get_temp_folder, __blog__
from src.pyquickhelper.pycode import get_call_stack


class TestTraceExecution(unittest.TestCase):

    def test_call_stack(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        res = get_call_stack()
        fLOG(res)
        assert len(res.split("\n")) > 2


if __name__ == "__main__":
    unittest.main()
