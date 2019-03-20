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

from pyquickhelper.loghelper import fLOG
from pyquickhelper.pycode import get_temp_folder, ExtTestCase
from pyquickhelper.filehelper import unzip_files


class TestCompressHelperBug2(ExtTestCase):

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
