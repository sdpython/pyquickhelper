"""
@brief      test log(time=4s)
"""

import sys
import os
import unittest
from pyquickhelper.pycode import get_temp_folder, ExtTestCase
from pyquickhelper.filehelper import un7zip_files
from pyquickhelper.pycode import skipif_azure_linux, skipif_appveyor, skipif_travis


class TestCompressHelperBug(ExtTestCase):

    @skipif_azure_linux('pylzma not available, must be installed from github')
    @skipif_appveyor('pylzma not available, must be installed from github')
    def test_uncompress_7zip_lzma2(self):
        import pylzma
        # use github version, not pypi version (2016-11-11)
        # this version does not include a fix to read file produced by the
        # latest version of 7z
        self.assertTrue(pylzma)

        fold = get_temp_folder(__file__, "temp_uncompress_7zip_lzma2")
        data = os.path.join(fold, "..", "data", "donnees.7z")
        self.assertExists(data)
        files = un7zip_files(data, where_to=fold)
        self.assertEqual(len(files), 1)
        self.assertTrue(files[0].endswith('donnees.txt'))

    @skipif_appveyor('pylzma not available, must be installed from github')
    @skipif_travis('command line not available')
    def test_uncompress_7zip_lzma2_cmd(self):
        import pylzma
        # use github version, not pypi version (2016-11-11)
        # this version does not include a fix to read file produced by the
        # latest version of 7z
        self.assertTrue(pylzma)

        fold = get_temp_folder(__file__, "temp_uncompress_7zip_lzma2_cmd")
        data = os.path.join(fold, "..", "data", "donnees.7z")
        self.assertExists(data)
        files = un7zip_files(data, where_to=fold, cmd_line=True)
        self.assertEqual(len(files), 1)
        self.assertTrue(files[0].endswith('donnees.txt'))


if __name__ == "__main__":
    unittest.main()
