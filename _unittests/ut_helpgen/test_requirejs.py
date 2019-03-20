"""
@brief      test log(time=7s)

skip this test for regular run
"""

import sys
import os
import unittest

from pyquickhelper.loghelper import fLOG
from pyquickhelper.pycode import get_temp_folder, ExtTestCase
from pyquickhelper.helpgen.install_custom import download_requirejs


class TestRequirejs(ExtTestCase):

    def test_download_requirejs(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        dest = get_temp_folder(__file__, "temp_install_requirejs_sphinx")
        fs = download_requirejs(dest, fLOG=fLOG)
        self.assertGreater(len(fs), 0)
        for a in fs:
            self.assertExists(a)
        r = os.path.join(dest, "require.js")
        self.assertExists(r)

    def test_download_requirejs_local(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        dest = get_temp_folder(__file__, "temp_install_requirejs_sphinx_local")
        fs = download_requirejs(dest, fLOG=fLOG, location=None)
        self.assertGreater(len(fs), 0)
        for a in fs:
            self.assertExists(a)
        r = os.path.join(dest, "require.js")
        self.assertExists(r)


if __name__ == "__main__":
    unittest.main()
