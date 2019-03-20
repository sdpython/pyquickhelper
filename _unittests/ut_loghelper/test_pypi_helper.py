"""
@brief      test log(time=42s)
"""

import sys
import os
import unittest
import datetime

if "temp_" in os.path.abspath(__file__):
    raise ImportError(
        "this file should not be imported in that location: " +
        os.path.abspath(__file__))

from pyquickhelper.loghelper import fLOG
from pyquickhelper.loghelper import enumerate_pypi_versions_date


class TestPypiHelper(unittest.TestCase):

    def test_clone_repo(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        iter = enumerate_pypi_versions_date('pyquickhelper')
        res = []
        for it in iter:
            res.append(it)
            if len(res) >= 2:
                break
        self.assertEqual(len(res), 2)
        self.assertIsInstance(res[0][0], datetime.datetime)
        self.assertGreater(res[0][2], 0)
        self.assertIn('.', res[0][1])


if __name__ == "__main__":
    unittest.main()
