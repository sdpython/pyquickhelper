"""
@brief      test log(time=2s)
@author     Xavier Dupre
"""

import sys
import os
import unittest
import random


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
from src.pyquickhelper.benchhelper import BenchMark


class TestBenchMark_(BenchMark):

    def init(self):
        pass

    def bench(self, **p):
        h = random.randint(1, 100)
        return dict(nb=h, value=p["value"], _btry=str(h)), dict(nb=h, script="a\nb", _btry=str(h))

    def end(self):
        pass


class TestBenchMark(unittest.TestCase):

    def test_benchmark(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        temp = get_temp_folder(__file__, "temp_benchmark")
        bench = TestBenchMark_("TestName", fLOG=fLOG, clog=temp)
        params = [dict(value=random.randint(10, 20)) for i in range(0, 100)]
        bench.run(params)
        df = bench.to_df()
        ht = df.to_html(float_format="%1.3f", index=False)
        assert len(df) > 0
        assert ht
        report = os.path.join(temp, "report.html")
        csv = os.path.join(temp, "report.csv")
        rst = os.path.join(temp, "report.rst")
        bench.report(filehtml=report, filecsv=csv, filerst=rst)
        assert os.path.exists(report)
        assert os.path.exists(csv)
        assert os.path.exists(rst)


if __name__ == "__main__":
    unittest.main()
