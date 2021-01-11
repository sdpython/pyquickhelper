"""
@brief      test log(time=2s)
@author     Xavier Dupre
"""

import sys
import os
import unittest
import warnings
import datetime
from io import StringIO

from pyquickhelper.loghelper import fLOG
from pyquickhelper.filehelper import TransferFTP, FolderTransferFTP, FileTreeNode
from pyquickhelper.pycode import is_travis_or_appveyor, get_temp_folder, ExtTestCase
from pyquickhelper.loghelper.os_helper import get_machine, get_user
from pyquickhelper.loghelper import get_password


class TestTransferFTPTrue(ExtTestCase):

    def get_web(self):
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', DeprecationWarning)
            import keyring
        prefix = "pyquickhelper2,"
        try:
            user = get_password("web", prefix + "user", ask=False)
            pwd = get_password("web", prefix + "pwd", ask=False)
            ftpsite = get_password("web", prefix + "ftp", ask=False)
        except RuntimeError:
            user = None
            pwd = None
        if user is None:
            if not is_travis_or_appveyor():
                zoo = []
                for k, v in sorted(os.environ.items()):
                    zoo.append("{0}={1}".format(k, v))
                raise Exception("user password is empty, prefix='{0}', username='{1}'\n{2}".format(
                    prefix, get_user(), "\n".join(zoo)))
            return None

        web = TransferFTP(ftpsite, user, pwd, fLOG=fLOG, ftps='SFTP')
        return web

    def test_transfer_sftp_true(self):
        fLOG(__file__, self._testMethodName, OutputPrint=__name__ == "__main__")

        web = self.get_web()
        if web is None:
            return
        pf = web.pwd()
        self.assertIn("home/", pf)
        r = web.ls(".")
        self.assertTrue(isinstance(r, list))
        web.close()
        fLOG([pf])

    def test_transfer_sftp_start_transfering(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        ftp = self.get_web()
        if ftp is None:
            return

        # Transfering
        now = datetime.datetime.now()
        temp = get_temp_folder(__file__, "temp_transfer_ftp_true")
        with open(os.path.join(temp, "essai.txt"), 'w') as f:
            f.write(str(now))

        sfile = os.path.join(temp, "status_ut.txt")
        ftn = FileTreeNode(temp)

        web = FolderTransferFTP(ftn, ftp, sfile,
                                root_web="/home/ftpuser/ftp/web/apptest",
                                fLOG=fLOG, exc=True)

        done = web.start_transfering(delay=0.1)
        ftp.close()

        names = [os.path.split(f.filename)[-1] for f in done]
        self.assertEqual(names, ['essai.txt'])

        # two, same file, should not be done again
        ftp = self.get_web()
        if ftp is None:
            return

        web = FolderTransferFTP(ftn, ftp, sfile,
                                root_web="/home/ftpuser/ftp/web/apptest/",
                                fLOG=fLOG)

        done = web.start_transfering(delay=0.1)
        ftp.close()
        self.assertEmpty(done)

        ftp = self.get_web()
        if ftp is None:
            return
        content = ftp.retrieve("/home/ftpuser/ftp/web/apptest/", "essai.txt")
        self.assertNotEmpty(content)
        ftp.close()


if __name__ == "__main__":
    unittest.main()
