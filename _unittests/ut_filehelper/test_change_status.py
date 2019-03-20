"""
@brief      test log(time=2s)
@author     Xavier Dupre
"""

import sys
import os
import unittest
import stat

from pyquickhelper.loghelper import fLOG
from pyquickhelper.pycode import get_temp_folder
from pyquickhelper.filehelper import change_file_status


class TestChangesStatus(unittest.TestCase):

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
        if sys.platform.startswith("win"):
            change_file_status(temp, strict=True)
        change_file_status(file)
        if sys.platform.startswith("win"):
            change_file_status(file, strict=True)
        change_file_status(file, strict=False,
                           status=stat.S_IREAD, include_folder=True)


if __name__ == "__main__":
    unittest.main()
