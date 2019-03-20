"""
@brief      test tree node (time=5s)
"""


import sys
import os
import unittest

from pyquickhelper.loghelper import fLOG
from pyquickhelper.pycode import add_missing_development_version


class TestReferences(unittest.TestCase):

    def test_references(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        paths = add_missing_development_version("pyquickhelper", __file__)
        assert len(paths) <= 1  # no added paths if no need to add a path


if __name__ == "__main__":
    unittest.main()
