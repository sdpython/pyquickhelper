"""
@brief      test log(time=2s)
@author     Xavier Dupre
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
from src.pyquickhelper.filehelper import TransferFTP
from src.pyquickhelper.pycode import is_travis_or_appveyor
from src.pyquickhelper.loghelper.os_helper import get_machine


class TestTransferFTPTrue(unittest.TestCase):

    def test_transfer_ftp_true(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        if sys.version_info[0] < 3:
            warnings.warn(
                "No testing transfer FTP on Python 2.7 (issue with str and bytes)")
            return
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', DeprecationWarning)
            import keyring
        machine = get_machine()
        try:
            user = keyring.get_password("web", machine + "user")
            pwd = keyring.get_password("web", machine + "pwd")
        except RuntimeError:
            user = None
            pwd = None
        if user is None:
            if not is_travis_or_appveyor():
                raise Exception("user password is empty, machine='{0}', username='{1}'".format(
                    machine, os.environ.get("USERNAME", None)))
            else:
                return

        web = TransferFTP("ftp.xavierdupre.fr", user, pwd, fLOG=fLOG)
        r = web.ls(".")
        fLOG(r)
        self.assertTrue(isinstance(r, list))
        web.close()


if __name__ == "__main__":
    unittest.main()
