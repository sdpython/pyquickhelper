"""
@brief      test log(time=1s)

"""


import sys
import os
import unittest

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

from src.pyquickhelper import fLOG
from src.pyquickhelper.serverdoc import get_jenkins_mappings


class TestMappings(unittest.TestCase):

    def test_mappings(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        path = os.path.abspath(os.path.split(__file__)[0])
        data = os.path.join(path, "data")
        fold = os.path.normpath(os.path.join(path, ".."))
        fLOG(fold)
        res = get_jenkins_mappings(fold, loc="data2")
        fLOG(res)
        assert len(res) > 0


if __name__ == "__main__":
    unittest.main()
