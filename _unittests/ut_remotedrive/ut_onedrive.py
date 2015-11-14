"""
@brief      test log(time=0s)
"""

import sys
import os
import unittest
import re
import flake8
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

from src.pyquickhelper import __version__, fLOG
from src.pyquickhelper.remotedrive import OneDrive


class TestOneDrive(unittest.TestCase):

    def test_onedrive(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        # does not work
        return

        # something like "00000000xxxxxx"
        user = os.environ.get("ONEDRIVEUSER", None)
        # something like "W2muxxxxx-IAsXboEsr2xxxxx"
        pwd = os.environ.get("ONEDRIVEPWD", None)
        one = OneDrive(user, pwd, fLOG=fLOG)
        one.connect()

        b = bytes([1, 4, 5, 2])
        tt = "pyquickhelper/unitest/file.bin"
        one.upload_data(tt, b)
        dd = one.download_data(tt)
        self.assertEqual(b, dd)


if __name__ == "__main__":
    unittest.main()
