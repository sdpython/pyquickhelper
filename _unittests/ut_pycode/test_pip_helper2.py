"""
@brief      test tree node (time=2s)
"""

import sys
import os
import unittest
import pandas

from pyquickhelper.loghelper import fLOG
from pyquickhelper.pycode.pip_helper import get_package_info
from pyquickhelper.pycode import ExtTestCase


class TestPipHelper2(ExtTestCase):

    def test_pip_show(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        info = get_package_info("pandas")
        # if "license" not in info:
        #    raise Exception(str(info))
        if "version" not in str(info):
            raise Exception(str(info))

        info = get_package_info("sphinx")
        if "version" not in str(info):
            raise Exception(str(info))

    def test_pip_show_all(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        info = get_package_info(start=0, end=2)
        df = pandas.DataFrame(info)
        self.assertNotEmpty(info)

        if __name__ == "__mahin__":
            info = get_package_info()
            df = pandas.DataFrame(info)
            df.to_excel("out_packages.xlsx")


if __name__ == "__main__":
    unittest.main()
