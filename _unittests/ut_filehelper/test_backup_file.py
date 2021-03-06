"""
@brief      test log(time=2s)
@author     Xavier Dupre
"""

import sys
import os
import unittest

from pyquickhelper.loghelper import fLOG
from pyquickhelper.pycode import get_temp_folder, ExtTestCase
from pyquickhelper.filehelper import EncryptedBackup, FileTreeNode, TransferAPIFile
from pyquickhelper.filehelper.transfer_api import MockTransferAPI


class TestBackupFiles(ExtTestCase):

    def test_backup(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        try:
            import Crypto as skip_
            algo = "AES"
        except ImportError:
            algo = "fernet"

        temp = get_temp_folder(__file__, "temp_backup_files")

        root = os.path.normpath(os.path.join(temp, ".."))
        fLOG(root)

        api = MockTransferAPI()
        ft = FileTreeNode(root, filter=".*[.]py", repository=False)
        enc = EncryptedBackup(
            key=b"unit" * 8,
            file_tree_node=ft,
            transfer_api=api,
            file_status=os.path.join(temp, "status.txt"),
            file_map=os.path.join(temp, "mapping.txt"),
            root_local=os.path.join(temp, "..", ".."),
            threshold_size=2000,
            fLOG=fLOG,
            algo=algo)

        done, issue = enc.start_transfering()
        self.assertNotEmpty(done)
        self.assertEmpty(issue)

        for k, v in sorted(enc.Mapping.items()):
            fLOG(k, len(v.pieces), v)

        enc.load_mapping()
        outfile = os.path.join(temp, "backed_test_backup_file.py")
        fpth = "ut_filehelper\\test_backup_file.py"
        if not sys.platform.startswith("win"):
            fpth = fpth.replace("\\", "/")
        enc.retrieve(fpth, filename=outfile)

        with open(outfile, "r") as f:
            c2 = f.read()
        with open(__file__.replace(".pyc", ".py"), "r") as f:
            c1 = f.read()
        self.assertEqual(c1, c2)

    def test_backup_file(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        try:
            import Crypto as skip__
            algo = "AES"
        except ImportError:
            algo = "fernet"

        temp = get_temp_folder(__file__, "temp_backup_files_file")

        root = os.path.normpath(os.path.join(temp, ".."))
        fLOG(root)

        api = TransferAPIFile(os.path.join(temp, "backup"))
        ft = FileTreeNode(root, filter=".*[.]py", repository=False)
        enc = EncryptedBackup(
            key=b"unit" * 8,
            file_tree_node=ft,
            transfer_api=api,
            file_status=os.path.join(temp, "status.txt"),
            file_map=os.path.join(temp, "mapping.txt"),
            root_local=os.path.join(temp, "..", ".."),
            threshold_size=2000,
            fLOG=fLOG,
            algo=algo)

        done, issue = enc.start_transfering()
        self.assertNotEmpty(done)
        self.assertEmpty(issue)

        for k, v in sorted(enc.Mapping.items()):
            fLOG(k, len(v.pieces), v)

        enc.load_mapping()
        outfile = os.path.join(temp, "backed_test_backup_file.py")
        fpth = "ut_filehelper\\test_backup_file.py"
        if not sys.platform.startswith("win"):
            fpth = fpth.replace("\\", "/")
        s = enc.retrieve(fpth, filename=outfile)

        with open(outfile, "r") as f:
            c2 = f.read()
        with open(__file__.replace(".pyc", ".py"), "r") as f:
            c1 = f.read()
        self.assertEqual(c1, c2)

        detemp = os.path.join(temp, "retrieved")
        s = enc.retrieve_all(detemp, regex=".*[.]py")
        self.assertNotEmpty(s)


if __name__ == "__main__":
    unittest.main()
