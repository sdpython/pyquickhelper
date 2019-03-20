"""
@brief      test tree node (time=5s)
"""


import sys
import os
import unittest

from pyquickhelper.loghelper import fLOG
from pyquickhelper.pycode.insetup_helper import _filter_out_warning, must_build


class TestInSetupHelper(unittest.TestCase):

    def test__filter_out_warning(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        out = "importlib\\_bootstrap.py:205: ImportWarning: can't resolve package from __spec__ " + \
              "or __package__, falling back on __name__ and __path__\n" + \
              "  return f(*args, **kwds)\n"
        new_out = _filter_out_warning(out)
        self.assertEqual(new_out.strip(), "")

    def test_must_build(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        self.assertTrue(must_build(["unittests"]))
        self.assertTrue(not must_build(["unittests2"]))


if __name__ == "__main__":
    unittest.main()
