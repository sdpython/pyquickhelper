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
            "src",
            "pyquickhelper",
            "__init__.py")
        with open(setup, "r") as f:
            c = f.read()
        reg = re.compile("__version__ = \\\"(.*)\\\"")

        f = reg.findall(c)
        if len(f) != 1:
            raise Exception("not only one version: {}".format(f))
        self.assertEqual(f[0].split('.')[:2], __version__.split('.')[:2])


if __name__ == "__main__":
    unittest.main()
