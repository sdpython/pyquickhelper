"""
@brief      test log(time=2s)
@author     Xavier Dupre
"""

import sys
import os
import unittest
import stat


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
from src.pyquickhelper.pycode import get_temp_folder, is_travis_or_appveyor
from src.pyquickhelper.filehelper import change_file_status


class TestChangesStatus(unittest.TestCase):

    def test_src_import(self):
        """for pylint"""
        self.assertTrue(src is not None)

    def test_change_status(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        temp = get_temp_folder(__file__, "temp_change_status")
        file = os.path.join(temp, "change.txt")
        with open(file, "w") as f:
            f.write("ah")
        change_file_status(temp)
        if is_travis_or_appveyor() not in ('circleci', 'travis'):
            change_file_status(temp, strict=True)
        change_file_status(file)
        if is_travis_or_appveyor() not in ('circleci', 'travis'):
            change_file_status(file, strict=True)
        change_file_status(file, strict=False,
                           status=stat.S_IREAD, include_folder=True)


if __name__ == "__main__":
    unittest.main()
