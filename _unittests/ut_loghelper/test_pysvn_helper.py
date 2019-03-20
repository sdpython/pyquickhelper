"""
@brief      test log(time=3s)
"""


import sys
import os
import unittest

from pyquickhelper.loghelper.flog import fLOG
from pyquickhelper.loghelper.pyrepo_helper import SourceRepository


class TestPySvnHelper (unittest.TestCase):

    def test_repo_version(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        path = os.path.split(__file__)[0]
        data = os.path.abspath(os.path.join(path, "..", ".."))
        s = SourceRepository()
        alls = s.version(data)
        fLOG("data", data)
        fLOG("version", alls)
        assert isinstance(alls, (int, str))


if __name__ == "__main__":
    unittest.main()
