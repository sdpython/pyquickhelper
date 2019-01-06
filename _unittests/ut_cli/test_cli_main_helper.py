"""
@brief      test tree node (time=7s)
"""


import sys
import os
import unittest
from io import StringIO

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
from src.pyquickhelper.pycode import ExtTestCase
from src.pyquickhelper.__main__ import main


class TempBuffer:
    "simple buffer"

    def __init__(self):
        "constructor"
        self.buffer = StringIO()

    def fprint(self, *args, **kwargs):
        "print function"
        mes = " ".join(str(_) for _ in args)
        self.buffer.write(mes)
        self.buffer.write("\n")

    def __str__(self):
        "usual"
        return self.buffer.getvalue()


class TestCliMainHelper(ExtTestCase):

    def test_src_import(self):
        """for pylint"""
        self.assertTrue(src is not None)

    def test_main(self):

        st = TempBuffer()
        main(args=[], fLOG=st.fprint)
        res = str(st)
        self.assertIn("python -m pyquickhelper <command>", res)
        self.assertIn("Synchronizes a folder", res)

        st = TempBuffer()
        main(args=["clean_files", "--help"], fLOG=st.fprint)
        res = str(st)
        self.assertIn("usage: clean_files", res)

        st = TempBuffer()
        main(args=["df2rst", "--help"], fLOG=st.fprint)
        res = str(st)
        self.assertIn(
            "usage: df2rst [-h] [--df DF] [-a ADD_LINE] [-al ALIGN] [-c COLUMN_SIZE]", res)

        st = TempBuffer()
        main(args=["encrypt", "--help"], fLOG=st.fprint)
        res = str(st)
        self.assertIn(
            "usage: encrypt [-h] [-s STATUS] [-m MAP] source dest password", res)

        st = TempBuffer()
        main(args=["encrypt_file", "--help"], fLOG=st.fprint)
        res = str(st)
        self.assertIn("usage: encrypt_file [-h] source dest password", res)

        st = TempBuffer()
        main(args=["encrypts", "--help"], fLOG=st.fprint)
        res = str(st)
        self.assertIn("Command not found: 'encrypts'.", res)

        st = TempBuffer()
        main(args=["synchronize_folder", "--help"], fLOG=st.fprint)
        res = str(st)
        self.assertIn(
            "synchronize_folder [-h] [--p1 P1] [--p2 P2] [-ha HASH_SIZE]", res)

        st = TempBuffer()
        main(args=["process_notebooks", "--help"], fLOG=st.fprint)
        res = str(st)
        self.assertIn(
            "process_notebooks [-h] [-n NOTEBOOKS] [-o OUTFOLD] [-b BUILD]", res)

    def test_main_epkg(self):
        st = TempBuffer()
        main(args=["clean_files", "--help"], fLOG=st.fprint)
        res = str(st)
        self.assertNotIn("<<", res)
        self.assertNotIn("``", res)
        self.assertIn("`'\\n'`", res)


if __name__ == "__main__":
    unittest.main()
