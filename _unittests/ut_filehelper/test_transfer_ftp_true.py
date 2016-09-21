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
from src.pyquickhelper.filehelper import TransferFTP
from src.pyquickhelper.pycode import is_travis_or_appveyor


class TestTransferFTPTrue(unittest.TestCase):

    def test_transfer_ftp_true(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        import keyring
        machine = os.environ.get("COMPUTERNAME", os.environ.get("HOSTNAME", "CI"))
        try:
            user = keyring.get_password("web", machine + "user")
            pwd = keyring.get_password("web", machine + "pwd")
        except RuntimeError:
            user = None
            pwd = None
        if user is None:
            if not is_travis_or_appveyor():
                raise Exception("user password is empty")
            else:
                return

        web = TransferFTP("ftp.xavierdupre.fr", user, pwd, fLOG=fLOG)
        r = web.ls(".")
        fLOG(r)
        assert isinstance(r, list)

if __name__ == "__main__":
    unittest.main()
