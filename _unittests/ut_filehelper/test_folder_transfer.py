"""
@brief      test log(time=2s)
"""

import sys
import os
import unittest

if "temp_" in os.path.abspath(__file__):
    raise ImportError(
        "this file should not be imported in that location: " +
        os.path.abspath(__file__))

from pyquickhelper.pycode import get_temp_folder
from pyquickhelper.loghelper import fLOG
from pyquickhelper.filehelper import FileTreeNode, FolderTransferFTP
from pyquickhelper.filehelper.ftp_transfer_mock import MockTransferFTP


class TestFolderTransfer(unittest.TestCase):

    def test_folder_transfer(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        temp = get_temp_folder(__file__, "temp_folder_transfer")
        status = os.path.join(temp, "temp_status_file.txt")
        folder = os.path.normpath(os.path.join(temp, "..", "..", "..", "src"))

        ftn = FileTreeNode(folder)
        ftp = MockTransferFTP(
            "http://www.xavierdupre.fr/",
            "login",
            "password",
            fLOG=fLOG)
        fftp = FolderTransferFTP(ftn, ftp, status,
                                 footer_html="<b>footer</b>",
                                 content_filter=lambda c, f, force_allow=False: c)

        li = list(fftp.iter_eligible_files())
        assert len(li) > 0

        done = fftp.start_transfering()
        assert len(done) > 0
        fLOG(done[0])
        fLOG(done)

        assert os.path.exists(status)

        done = fftp.start_transfering()
        if len(done) > 0:
            for f in done:
                fLOG(f)
            assert False

        ftp.close()


if __name__ == "__main__":
    unittest.main()
