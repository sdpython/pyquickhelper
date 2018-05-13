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
from src.pyquickhelper.filehelper import unzip_files


class TestCompressHelperBug2(ExtTestCase):

    def test_src_import(self):
        """for pylint"""
        self.assertTrue(src is not None)

    def test_unzip_bug(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        fold = get_temp_folder(__file__, "temp_unzip_bug")
        data = os.path.join(fold, "..", "data", "dada.zip")
        self.assertExists(data)
        files = unzip_files(data, where_to=fold,
                            fLOG=fLOG, fail_if_error=False)
        self.assertEqual(len(files), 5)


if __name__ == "__main__":
    unittest.main()
