"""
@brief      test tree node (time=5s)
"""


import sys
import os
import unittest
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

from src.pyquickhelper.loghelper import fLOG
from src.pyquickhelper.pycode import clean_files, ExtTestCase, get_temp_folder


class TestCleanFile(ExtTestCase):

    def test_clean_file_cr(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        folder = os.path.abspath(os.path.dirname(__file__))
        self.assertRaise(lambda: clean_files(folder, op="op"), ValueError)
        res = clean_files(folder, fLOG=fLOG, posreg="test_clean.*[.]py$")
        self.assertEmpty(res)

    def test_clean_file_cr_nefg_pattern(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        temp = get_temp_folder(__file__, "temp_clean_neg_pattern")
        name1 = os.path.join(temp, "cool.txt")
        with open(name1, "w") as f:
            f.write("t\r\nv\r\n")
        git = os.path.join(temp, ".git")
        os.mkdir(git)
        name2 = os.path.join(git, "cool.txt")
        with open(name2, "wb") as f:
            f.write(b"T\r\nV\r\n")
        with open(name2, "rb") as f:
            c2exp = f.read()
        folder = temp
        res = clean_files(folder, fLOG=fLOG, posreg='.*')
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0], "cool.txt")
        with open(name1, "r") as f:
            c1 = f.read()
        with open(name2, "rb") as f:
            c2 = f.read()
        self.assertEqual(c1, "t\nv\n")
        self.assertEqual(c2, b"T\r\nV\r\n")

    def test_clean_file_pep8(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        folder = os.path.abspath(os.path.dirname(__file__))
        res = clean_files(folder, fLOG=fLOG,
                          posreg="test_clean.*[.]py$", op='pep8')
        self.assertEmpty(res)


if __name__ == "__main__":
    unittest.main()
