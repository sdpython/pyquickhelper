"""
@brief      test tree node (time=15s)
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

from src.pyquickhelper import fLOG, get_temp_folder, run_cmd
from src.pyquickhelper import py3to2_convert_tree, py3to2_convert


class TestPy3to2Bug(unittest.TestCase):

    def test_py3to2_bug(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        if sys.version_info[0] == 2:
            return

        #temp = get_temp_folder(__file__, "temp_py3to2_bug")
        root = os.path.abspath(os.path.dirname(__file__))
        file = os.path.normpath(
            os.path.join(root, "data", "2test_download_pip.py"))
        conv = py3to2_convert(file, ["pyquickhelper"])
        if 'assert "..", "pyquickhelper"' in conv:
            raise Exception(conv)


if __name__ == "__main__":
    unittest.main()
