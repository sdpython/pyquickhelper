"""
@brief      test log(time=2s)
@author     Xavier Dupre
"""

import sys
import os
import unittest
import warnings
import datetime

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
from src.pyquickhelper.filehelper import TransferFTP, FolderTransferFTP, FileTreeNode
from src.pyquickhelper.pycode import is_travis_or_appveyor, get_temp_folder, ExtTestCase
from src.pyquickhelper.loghelper.os_helper import get_machine, get_user


class TestTransferFTPTrue(ExtTestCase):

    def test_src_import(self):
        """for pylint"""
        self.assertTrue(src is not None)

    @unittest.skipIf(sys.version_info[0] == 2, "issue with strings")
    def test_transfer_ftp_true(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        with warnings.catch_warnings():
            warnings.simplefilter('ignore', DeprecationWarning)
            import keyring
        prefix = "pyquickhelper,"
        try:
            user = keyring.get_password("web", prefix + "user")
            pwd = keyring.get_password("web", prefix + "pwd")
        except RuntimeError:
            user = None
            pwd = None
        if user is None:
            if not is_travis_or_appveyor():
                raise Exception("user password is empty, prefix='{0}', username='{1}'".format(
                    prefix, get_user()))
            else:
                return

        web = TransferFTP("ftp.xavierdupre.fr", user, pwd, fLOG=fLOG)
        r = web.ls(".")
        fLOG(r)
        self.assertTrue(isinstance(r, list))
        web.close()

    @unittest.skipIf(sys.version_info[0] == 2, "issue with strings")
    def test_transfer_ftp_start_transfering(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        with warnings.catch_warnings():
            warnings.simplefilter('ignore', DeprecationWarning)
            import keyring
        prefix = "pyquickhelper,"
        try:
            user = keyring.get_password("web", prefix + "user")
            pwd = keyring.get_password("web", prefix + "pwd")
        except RuntimeError:
            user = None
            pwd = None
        if user is None:
            if not is_travis_or_appveyor():
                raise Exception("user password is empty, prefix='{0}', username='{1}'".format(
                    prefix, get_user()))
            else:
                return

        # Transfering
        now = datetime.datetime.now()
        temp = get_temp_folder(__file__, "temp_transfer_ftp_true")
        with open(os.path.join(temp, "essai.txt"), 'w') as f:
            f.write(str(now))

        sfile = os.path.join(temp, "status_ut.txt")
        ftn = FileTreeNode(temp)

        # one
        ftp = TransferFTP("ftp.xavierdupre.fr", user, pwd, fLOG=fLOG)

        web = FolderTransferFTP(ftn, ftp, sfile,
                                root_web="/www/htdocs/apptest/",
                                fLOG=fLOG)

        done = web.start_transfering(delay=0.1)
        ftp.close()
        names = [os.path.split(f.filename)[-1] for f in done]
        self.assertEqual(names, ['essai.txt'])

        # two, same file, should not be done again
        ftp = TransferFTP("ftp.xavierdupre.fr", user, pwd, fLOG=fLOG)

        web = FolderTransferFTP(ftn, ftp, sfile,
                                root_web="/www/htdocs/apptest/",
                                fLOG=fLOG)

        done = web.start_transfering(delay=0.1)
        ftp.close()
        self.assertEmpty(done)


if __name__ == "__main__":
    unittest.main()
