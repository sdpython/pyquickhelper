"""
@brief      test log(time=2s)
"""

import sys
import os
import unittest
import pandas

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
from src.pyquickhelper.filehelper import is_file_string
from src.pyquickhelper.pandashelper import read_csv


class TestPandasHelperZip(unittest.TestCase):

    def test_zip_to_df(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        dirname = os.path.abspath(os.path.dirname(__file__))
        name = os.path.join(dirname, "data", "mynotebooks.zip")
        self.assertEqual(os.path.exists(name), True)
        self.assertEqual(is_file_string(name), True)
        dfs = read_csv(name, encoding="utf8",
                       fvalid=lambda n: n != 'bank-names.txt')
        assert isinstance(dfs, dict)
        self.assertEqual(len(dfs), 3)
        fLOG(list(dfs.keys()))
        full = dfs["bank-full.csv"]
        assert isinstance(full, pandas.DataFrame)


if __name__ == "__main__":
    unittest.main()
