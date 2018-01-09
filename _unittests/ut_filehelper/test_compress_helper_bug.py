"""
@brief      test log(time=4s)
"""

import sys
import os
import unittest

if "temp_" in os.path.abspath(__file__):
    raise ImportError(
        "this file should not be imported in that location: " +
        os.path.abspath(__file__))

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
from src.pyquickhelper.pycode import get_temp_folder, ExtTestCase
from src.pyquickhelper.filehelper import un7zip_files
from src.pyquickhelper.pycode import is_travis_or_appveyor


class TestCompressHelperBug(ExtTestCase):

    def test_uncompress_7zip_lzma2(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        if is_travis_or_appveyor() in ('circleci', 'travis'):
            # 7z not available
            return
        import pylzma
        # use github version, not pypi version (2016-11-11)
        # this version does not include a fix to read file produced by the
        # latest version of 7z
        self.assertTrue(pylzma)

        fold = get_temp_folder(__file__, "temp_uncompress_7zip_lzma2")
        data = os.path.join(fold, "..", "data", "donnees.7z")
        self.assertExists(data)
        files = un7zip_files(data, where_to=fold, fLOG=fLOG)
        self.assertEqual(len(files), 1)
        self.assertTrue(files[0].endswith('donnees.txt'))

    def test_uncompress_7zip_lzma2_cmd(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        if is_travis_or_appveyor() in ('circleci', 'travis'):
            # 7z not available
            return
        import pylzma
        # use github version, not pypi version (2016-11-11)
        # this version does not include a fix to read file produced by the
        # latest version of 7z
        self.assertTrue(pylzma)

        fold = get_temp_folder(__file__, "temp_uncompress_7zip_lzma2_cmd")
        data = os.path.join(fold, "..", "data", "donnees.7z")
        self.assertExists(data)
        files = un7zip_files(data, where_to=fold, fLOG=fLOG, cmd_line=True)
        self.assertEqual(len(files), 1)
        self.assertTrue(files[0].endswith('donnees.txt'))


if __name__ == "__main__":
    unittest.main()
