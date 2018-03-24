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
from src.pyquickhelper.loghelper import enumerate_pypi_versions_date


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
