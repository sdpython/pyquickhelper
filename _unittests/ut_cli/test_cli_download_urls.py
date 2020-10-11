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


class TestCliDownloadUrls(ExtTestCase):

    def test_download_urls_in_folder_content(self):
        st = BufferedPrint()
        main(args=['download_urls_in_folder_content', '--help'], fLOG=st.fprint)
        res = str(st)
        self.assertIn("download_urls_in_folder_content [-h]", res)


if __name__ == "__main__":
    unittest.main()
