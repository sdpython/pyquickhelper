"""
@brief      test log(time=0s)
"""

import sys
import os
import unittest
import re

from pyquickhelper import __version__
from pyquickhelper.loghelper import fLOG


class TestVersion (unittest.TestCase):

    def test_version(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        setup = os.path.join(
            os.path.split(__file__)[0],
            "..",
            "..",
            "setup.py")
        with open(setup, "r") as f:
            c = f.read()
        reg = re.compile("sversion *= \\\"(.*)\\\"")

        f = reg.findall(c)
        if len(f) != 1:
            raise Exception("not only one version")
        assert f[0] == __version__


if __name__ == "__main__":
    unittest.main()
