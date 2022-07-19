"""
@brief      test log(time=1s)

"""


import sys
import os
import unittest

from pyquickhelper.loghelper import fLOG
from pyquickhelper.server import get_jenkins_mappings


class TestMappings(unittest.TestCase):

    def test_mappings(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        path = os.path.abspath(os.path.split(__file__)[0])
        fold = os.path.normpath(os.path.join(path, ".."))
        fold = os.path.normpath(fold)
        fLOG(fold)
        res = get_jenkins_mappings(fold, loc="data2")
        if len(res) <= 0 and sys.version_info[0] != 2:
            raise Exception(f"{res} - {fold}")


if __name__ == "__main__":
    unittest.main()
