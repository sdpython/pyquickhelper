"""
@brief      test log(time=7s)

skip this test for regular run
"""

import sys
import os
import unittest

from pyquickhelper.loghelper import fLOG
from pyquickhelper.pycode import get_temp_folder
from pyquickhelper.helpgen.install_custom import download_revealjs


class TestRevealjs(unittest.TestCase):

    def test_install_revealjs_github(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        temp = get_temp_folder(__file__, "temp_install_revealjs_github")
        dest = get_temp_folder(__file__, "temp_install_revealjs_github_dest")
        fs = download_revealjs(temp, dest, fLOG=fLOG)
        fLOG(fs)
        assert len(fs) > 0
        for a in fs:
            assert os.path.exists(a)


if __name__ == "__main__":
    unittest.main()
