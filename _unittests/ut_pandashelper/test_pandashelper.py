"""
@brief      test log(time=2s)
"""

import os
import unittest
import numpy
from pandas import read_csv

from pyquickhelper.loghelper import fLOG
from pyquickhelper.pandashelper import isempty, isnan


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
                df = read_csv(url, sep="\t", names=[
                    "ville", "annee", "temps", "secondes"])
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
