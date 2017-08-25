"""
@brief      test log(time=2s)
"""

import sys
import os
import unittest
import numpy


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
from src.pyquickhelper.pandashelper import isempty, isnan, read_url


if sys.version_info[0] == 2:
    ConnectionResetError = Exception


class TestPandasHelper(unittest.TestCase):

    def test_version(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        url = "http://www.xavierdupre.fr/enseignement/complements/marathon.txt"
        repeat = 0
        while True:
            try:
                df = read_url(
                    url,
                    sep="\t",
                    names=[
                        "ville",
                        "annee",
                        "temps",
                        "secondes"])
                break
            except ConnectionResetError as e:
                if repeat >= 2:
                    raise e
                repeat += 1
        self.assertTrue(len(df) > 0)
        self.assertEqual(len(df.columns), 4)
        fLOG(df.head())

    def test_isnull(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        self.assertTrue(isempty(""))
        self.assertTrue(not isempty("e"))
        self.assertTrue(isempty(None))
        self.assertTrue(isempty(numpy.nan))

        self.assertTrue(isnan(numpy.nan))
        self.assertTrue(not isnan(0.0))


if __name__ == "__main__":
    unittest.main()
