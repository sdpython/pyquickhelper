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

    def test_clean_files(self):
        st = BufferedPrint()
        main(args=["clean_files", "--help"], fLOG=st.fprint)
        res = str(st)
        self.assertIn("usage: clean_files", res)

    def test_df2rst(self):
        st = BufferedPrint()
        main(args=["df2rst", "--help"], fLOG=st.fprint)
        res = str(st)
        self.assertIn(
            "usage: df2rst", res)

    def test_encrypt(self):
        st = BufferedPrint()
        main(args=["encrypt", "--help"], fLOG=st.fprint)
        res = str(st)
        self.assertIn("usage: encrypt", res)

    def test_encrypt_files(self):
        st = BufferedPrint()
        main(args=["encrypt_file", "--help"], fLOG=st.fprint)
        res = str(st)
        self.assertIn("usage: encrypt_file", res)

    def test_encrypts(self):
        st = BufferedPrint()
        main(args=["encrypts", "--help"], fLOG=st.fprint)
        res = str(st)
        self.assertIn("Command not found: 'encrypts'.", res)

    def test_sync(self):
        st = BufferedPrint()
        main(args=["synchronize_folder", "--help"], fLOG=st.fprint)
        res = str(st)
        self.assertIn("usage: synchronize_folder", res)

    def test_cvtnb(self):
        st = BufferedPrint()
        main(args=["convert_notebook", "--help"], fLOG=st.fprint)
        res = str(st)
        self.assertIn("usage: convert_notebook", res)

    def test_runnb(self):
        st = BufferedPrint()
        main(args=["run_notebook", "--help"], fLOG=st.fprint)
        res = str(st)
        self.assertIn("usage: run_notebook", res)

    def test_vdiff(self):
        st = BufferedPrint()
        main(args=["visual_diff", "--help"], fLOG=st.fprint)
        res = str(st)
        self.assertIn("usage: visual_diff", res)

    def test_ls(self):
        st = BufferedPrint()
        main(args=["ls", "--help"], fLOG=st.fprint)
        res = str(st)
        self.assertIn("usage: ls", res)

    def test_rtf(self):
        st = BufferedPrint()
        main(args=["run_test_function", "--help"], fLOG=st.fprint)
        res = str(st)
        self.assertIn("usage: run_test_function", res)

    def test_srst(self):
        st = BufferedPrint()
        main(args=["sphinx_rst", "--help"], fLOG=st.fprint)
        res = str(st)
        self.assertIn("usage: sphinx_rst", res)

    def test_runnb2(self):
        st = BufferedPrint()
        main(args=["run_notebook", "--help"], fLOG=st.fprint)
        res = str(st)
        self.assertIn("usage: run_notebook", res)

    def test_repeat(self):
        st = BufferedPrint()
        main(args=["repeat_script", "--help"], fLOG=st.fprint)
        res = str(st)
        self.assertIn("usage: repeat_script", res)

    def test_ftp(self):
        st = BufferedPrint()
        main(args=["ftp_upload", "--help"], fLOG=st.fprint)
        res = str(st)
        self.assertIn("usage: ftp_upload", res)

    def test_main_epkg(self):
        st = BufferedPrint()
        main(args=["clean_files", "--help"], fLOG=st.fprint)
        res = str(st)
        self.assertNotIn("<<", res)


if __name__ == "__main__":
    unittest.main()
