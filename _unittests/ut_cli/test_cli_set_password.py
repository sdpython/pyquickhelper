"""
@brief      test tree node (time=7s)
"""

import sys
import os
import unittest
import warnings
from io import StringIO

from pyquickhelper.loghelper import fLOG, BufferedPrint
from pyquickhelper.pycode import ExtTestCase, get_temp_folder
from pyquickhelper.__main__ import main


class TestCliSetPassword(ExtTestCase):

    def test_set_passwrd(self):
        st = BufferedPrint()
        main(args=['set_password', '--help'], fLOG=st.fprint)
        res = str(st)
        self.assertIn("usage: set_password", res)


if __name__ == "__main__":
    unittest.main()
