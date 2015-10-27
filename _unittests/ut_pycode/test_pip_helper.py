"""
@brief      test tree node (time=2s)
"""

import sys
import os
import unittest
import re
import shutil
import warnings
import pandas

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

from src.pyquickhelper import fLOG, is_travis_or_appveyor
from src.pyquickhelper.pycode.pip_helper import get_packages_list, get_package_info, package2dict


class TestPipHelper(unittest.TestCase):

    def test_pip_list(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        li = get_packages_list()
        dt = package2dict(li[0])
        for k, v in dt.items():
            fLOG(k, v)
        assert len(li) > 0

    def test_pip_show(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        info = get_package_info("pandas")
        # if "license" not in info:
        #    raise Exception(str(info))
        if "version" not in info:
            raise Exception(str(info))

        if is_travis_or_appveyor() != "travis" and sys.version_info[0] >= 3:
            info = get_package_info("sphinx")
            # if "license" not in info:
            #    raise Exception(str(info))
            if "version" not in info:
                raise Exception(str(info))

    def test_pip_show_all(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        info = get_package_info(start=0, end=2)
        df = pandas.DataFrame(info)
        assert len(info) > 0
        assert isinstance(info[0], dict)

        if __name__ == "__mahin__":
            info = get_package_info(fLOG=fLOG)
            df = pandas.DataFrame(info)
            df.to_excel("out_packages.xlsx")


if __name__ == "__main__":
    unittest.main()
