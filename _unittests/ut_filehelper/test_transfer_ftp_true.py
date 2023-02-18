"""
@brief      test log(time=2s)
@author     Xavier Dupre
"""

import os
import unittest
import warnings
import datetime
import ftplib
import socket
from pyquickhelper.loghelper import fLOG
from pyquickhelper.filehelper import TransferFTP, FolderTransferFTP, FileTreeNode
from pyquickhelper.pycode import is_travis_or_appveyor, get_temp_folder, ExtTestCase
from pyquickhelper.loghelper.os_helper import get_machine, get_user
from pyquickhelper.loghelper import get_password


class TestTransferFTPTrue(ExtTestCase):

    def test_transfer_ftp_true(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        prefix = "pyquickhelper,"
        try:
            user = get_password("web", prefix + "user", ask=False)
            pwd = get_password("web", prefix + "pwd", ask=False)
            ftpsite = get_password("web", prefix + "ftp", ask=False)
        except (RuntimeError, AttributeError):
            user = None
            pwd = None
        if user is None:
            if not is_travis_or_appveyor():
                zoo = []
                for k, v in sorted(os.environ.items()):
                    zoo.append(f"{k}={v}")
                raise AssertionError("user password is empty, prefix='{0}', username='{1}'\n{2}".format(
                    prefix, get_user(), "\n".join(zoo)))
            return

        try:
            web = TransferFTP(ftpsite, user, pwd, fLOG=fLOG)
        except ftplib.error_perm as e:
            if "Non-anonymous sessions must use encryption." in str(e):
                return
            raise e
        except ftplib.error_temp as e:
            if "421 Home directory not available" in str(e):
                return
            raise e
        except socket.gaierror as ee:
            if "Name or service not known" in str(ee):
                return
            if "getaddrinfo failed" in str(ee):
                return
            raise ee
        r = web.ls(".")
        fLOG(r)
        self.assertTrue(isinstance(r, list))
        web.close()

    def test_transfer_ftp_start_transfering(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        prefix = "pyquickhelper,"
        try:
            user = get_password("web", prefix + "user", ask=False)
            pwd = get_password("web", prefix + "pwd", ask=False)
            ftpsite = get_password("web", prefix + "ftp", ask=False)
        except (RuntimeError, AttributeError):
            user = None
            pwd = None
        if user is None:
            if not is_travis_or_appveyor():
                raise AssertionError("user password is empty, prefix='{0}', username='{1}'".format(
                    prefix, get_user()))
            return

        # Transfering
        now = datetime.datetime.now()
        temp = get_temp_folder(__file__, "temp_transfer_ftp_true")
        with open(os.path.join(temp, "essai.txt"), 'w') as f:
            f.write(str(now))

        sfile = os.path.join(temp, "status_ut.txt")
        ftn = FileTreeNode(temp)

        # one
        try:
            ftp = TransferFTP(ftpsite, user, pwd, fLOG=fLOG)
        except ftplib.error_perm as e:
            if "Non-anonymous sessions must use encryption." in str(e):
                return
            raise e
        except ftplib.error_temp as e:
            if "421 Home directory not available" in str(e):
                return
            raise e
        except socket.gaierror as ee:
            if "Name or service not known" in str(ee):
                return
            if "getaddrinfo failed" in str(ee):
                return
            raise ee

        web = FolderTransferFTP(ftn, ftp, sfile,
                                root_web="/www/htdocs/apptest/",
                                fLOG=fLOG)

        done = web.start_transfering(delay=0.1)
        ftp.close()
        names = [os.path.split(f.filename)[-1] for f in done]
        self.assertEqual(names, ['essai.txt'])

        # two, same file, should not be done again
        ftp = TransferFTP(ftpsite, user, pwd, fLOG=fLOG)

        web = FolderTransferFTP(ftn, ftp, sfile,
                                root_web="/www/htdocs/apptest/",
                                fLOG=fLOG)

        done = web.start_transfering(delay=0.1)
        ftp.close()
        self.assertEmpty(done)


if __name__ == "__main__":
    unittest.main()
