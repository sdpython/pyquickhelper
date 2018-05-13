"""
@brief      test log(time=2s)
"""

import sys
import os
import unittest
import datetime
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
from src.pyquickhelper.pycode import get_temp_folder


class TestPandasTennis(unittest.TestCase):

    def test_src_import(self):
        """for pylint"""
        self.assertTrue(src is not None)

    def test_pandas_tennis(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        days = ["lundi", "mardi", "mercredi",
                "jeudi", "vendredi", "samedi", "dimanche"]
        temp = get_temp_folder(__file__, "temp_pandas_tennis")
        rows = []
        dt = datetime.datetime.now()
        for i in range(0, 360):
            row = dict(date="%04d-%02d-%02d" % (dt.year, dt.month, dt.day),
                       jour=dt.weekday(),
                       journ=days[dt.weekday()])
            dt += datetime.timedelta(1)
            rows.append(row)

        df = pandas.DataFrame(rows)
        df["equipe"] = 0
        df.loc[(df.jour == 2) | (df.jour == 4), "equipe"] = 1
        df["equipe_sum"] = (df.equipe.cumsum() *
                            df["equipe"] + df["equipe"]) % 3
        df["equipe_sum"] += df["equipe"]
        fLOG(df.head(n=10))
        df.to_excel(os.path.join(temp, "tennis.xlsx"), index=False)


if __name__ == "__main__":
    unittest.main()
