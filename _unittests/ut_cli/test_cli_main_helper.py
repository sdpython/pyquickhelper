"""
@brief      test tree node (time=7s)
"""


import sys
import os
import unittest
from io import StringIO

from pyquickhelper.loghelper import fLOG, BufferedPrint
from pyquickhelper.pycode import ExtTestCase
from pyquickhelper.__main__ import main


class TestCliMainHelper(ExtTestCase):

    def test_main(self):

        st = BufferedPrint()
        main(args=[], fLOG=st.fprint)
        res = str(st)
        self.assertIn("python -m pyquickhelper <command>", res)
        self.assertIn("Synchronizes a folder", res)

        st = BufferedPrint()
        main(args=["clean_files", "--help"], fLOG=st.fprint)
        res = str(st)
        self.assertIn("usage: clean_files", res)

        st = BufferedPrint()
        main(args=["df2rst", "--help"], fLOG=st.fprint)
        res = str(st)
        self.assertIn(
            "usage: df2rst [-h] [--df DF] [-a ADD_LINE] [-al ALIGN] [-c COLUMN_SIZE]", res)

        st = BufferedPrint()
        main(args=["encrypt", "--help"], fLOG=st.fprint)
        res = str(st)
        self.assertIn(
            "usage: encrypt [-h] [-s STATUS] [-m MAP] source dest password", res)

        st = BufferedPrint()
        main(args=["encrypt_file", "--help"], fLOG=st.fprint)
        res = str(st)
        self.assertIn("usage: encrypt_file [-h] source dest password", res)

        st = BufferedPrint()
        main(args=["encrypts", "--help"], fLOG=st.fprint)
        res = str(st)
        self.assertIn("Command not found: 'encrypts'.", res)

        st = BufferedPrint()
        main(args=["synchronize_folder", "--help"], fLOG=st.fprint)
        res = str(st)
        self.assertIn(
            "synchronize_folder [-h] [--p1 P1] [--p2 P2] [-ha HASH_SIZE]", res)

        st = BufferedPrint()
        main(args=["process_notebooks", "--help"], fLOG=st.fprint)
        res = str(st)
        self.assertIn(
            "process_notebooks [-h] [-n NOTEBOOKS] [-o OUTFOLD] [-b BUILD]", res)

        st = BufferedPrint()
        main(args=["visual_diff", "--help"], fLOG=st.fprint)
        res = str(st)
        self.assertIn(
            "visual_diff [-h] [-f FILE1] [-fi FILE2]", res)

        st = BufferedPrint()
        main(args=["ls", "--help"], fLOG=st.fprint)
        res = str(st)
        self.assertIn(
            "ls [-h] [-f FOLDER] [-p PATTERN] [-n NEG_PATTERN]", res)

        st = BufferedPrint()
        main(args=["run_test_function", "--help"], fLOG=st.fprint)
        res = str(st)
        self.assertIn(
            "run_test_function [-h] [-m MODULE] [-p PATTERN] [-s STOP_FIRST]", res)

        st = BufferedPrint()
        main(args=["sphinx_rst", "--help"], fLOG=st.fprint)
        res = str(st)
        self.assertIn(
            "sphinx_rst [-h] [-i INPUT] [-w WRITER] [-k KEEP_WARNINGS]", res)

        st = BufferedPrint()
        main(args=["run_notebook", "--help"], fLOG=st.fprint)
        res = str(st)
        self.assertIn(
            "run_notebook [-h] [-f FILENAME] [-p PROFILE_DIR] [-w WORKING_DIR]", res)

        st = BufferedPrint()
        main(args=["repeat_script", "--help"], fLOG=st.fprint)
        res = str(st)
        self.assertIn(
            "epeat_script [-h] [-s SCRIPT] [-e EVERY_SECOND]", res)

    def test_main_epkg(self):
        st = BufferedPrint()
        main(args=["clean_files", "--help"], fLOG=st.fprint)
        res = str(st)
        self.assertNotIn("<<", res)
        self.assertNotIn("``", res)
        self.assertIn("`'\\n'`", res)


if __name__ == "__main__":
    unittest.main()
