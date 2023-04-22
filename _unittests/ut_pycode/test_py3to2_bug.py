"""
@brief      test tree node (time=15s)
"""


import sys
import os
import unittest

from pyquickhelper.loghelper import fLOG
from pyquickhelper.pycode.py3to2 import py3to2_convert


class TestPy3to2Bug(unittest.TestCase):

    def test_py3to2_bug(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        # temp = get_temp_folder(__file__, "temp_py3to2_bug")
        root = os.path.abspath(os.path.dirname(__file__))
        file = os.path.normpath(
            os.path.join(root, "data", "2test_download_pip.py"))
        conv = py3to2_convert(file, ["pyquickhelper"])
        if 'assert "..", "pyquickhelper"' in conv:
            raise Exception(conv)


if __name__ == "__main__":
    unittest.main()
