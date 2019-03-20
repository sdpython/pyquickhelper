"""
@brief      test log(time=8s)
@author     Xavier Dupre
"""

import sys
import os
import unittest
import shutil

from pyquickhelper.loghelper.flog import fLOG
from pyquickhelper.helpgen.post_process import post_process_rst_output


class TestRst(unittest.TestCase):

    def test_rst(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        path = os.path.abspath(os.path.split(__file__)[0])
        file = os.path.join(path, "data", "td1a_cenonce_session_10.rst")
        temp = os.path.join(path, "temp_rst")
        if not os.path.exists(temp):
            os.mkdir(temp)
        dest = os.path.join(temp, os.path.split(file)[-1])
        if os.path.exists(dest):
            os.remove(dest)
        shutil.copy(file, temp)
        post_process_rst_output(
            dest, False, False, False, False, False, fLOG=fLOG)


if __name__ == "__main__":
    unittest.main()
