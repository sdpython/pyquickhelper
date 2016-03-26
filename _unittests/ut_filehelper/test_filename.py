"""
@brief      test log(time=2s)
@author     Xavier Dupre
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
from src.pyquickhelper.filehelper import is_file_string


class TestFilename(unittest.TestCase):

    def test_filename(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        pos = ["c:\\test",
               "c:\\test.txt",
               "..",
               ".txt",
               "r.",
               "r",
               "mqldkfnqmodnsc/\\y"]

        for p in pos:
            if not is_file_string(p):
                raise Exception(p)

        neg = ["h\ng",
               "r\tr",
               "cd:ggd.h"]

        for p in neg:
            if is_file_string(p):
                raise Exception(p)


if __name__ == "__main__":
    unittest.main()
