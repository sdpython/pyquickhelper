"""
@brief      test tree node (time=7s)
"""


import os
import unittest
import socket

from pyquickhelper.loghelper import fLOG, BufferedPrint
from pyquickhelper.pycode import ExtTestCase
from pyquickhelper.__main__ import main


class TestCliFtp(ExtTestCase):

    def test_cli_ftp(self):
        st = BufferedPrint()
        try:
            main(args=['ftp_upload', '-f', '*.py', '-d', 'www/',
                       '-ho', 'ftp.xavierdupre.fr', '-u', 'user',
                       '--pwd', '***', '-ft', '1'],
                 fLOG=st.fprint)
        except socket.gaierror:
            # expected
            return

    def test_cli_ftp_comma(self):
        st = BufferedPrint()
        try:
            main(args=['ftp_upload', '-f', 'a,b', '-d', 'www/',
                       '-ho', 'ftp.xavierdupre.fr', '-u', 'user',
                       '--pwd', '***', '-ft', '1'],
                 fLOG=st.fprint)
        except socket.gaierror:
            # expected
            return


if __name__ == "__main__":
    unittest.main()
