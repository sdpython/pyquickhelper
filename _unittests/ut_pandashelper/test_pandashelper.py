"""
@brief      test log(time=2s)
"""

import sys
import os
import unittest
import re


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

from src.pyquickhelper import read_url, fLOG


class TestVersion (unittest.TestCase):

    def test_version(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        url = "http://www.xavierdupre.fr/enseignement/complements/marathon.txt"
        df = read_url(
            url,
            sep="\t",
            names=[
                "ville",
                "annee",
                "temps",
                "secondes"])
        assert len(df) > 0
        assert len(df.columns) == 4
        fLOG(df.head())


if __name__ == "__main__":
    unittest.main()
