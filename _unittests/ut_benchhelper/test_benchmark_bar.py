"""
@brief      test log(time=2s)
@author     Xavier Dupre
"""

import sys
import os
import unittest
import random
from tqdm import trange

from pyquickhelper.loghelper import fLOG
from pyquickhelper.pycode import get_temp_folder
from pyquickhelper.benchhelper import BenchMark


class ATestBenchMarkB_(BenchMark):

    def init(self):
        pass

    def bench(self, **p):
        h = random.randint(1, 100)
        return dict(nb=h, value=p["value"], _btry=str(h)), dict(nb=h, script="a\nb", _btry=str(h))

    def end(self):
        pass


class ATestBenchMarkB2_(BenchMark):

    def init(self):
        pass

    def bench(self, **p):
        h = random.randint(1, 100)
        return [(dict(nb=h, value=p["value"], _btry=str(h)), dict(nb=h, script="a\nb", _btry=str(h)))]

    def end(self):
        pass


class TestBenchMarkBar(unittest.TestCase):

    def test_benchmark_list_progressbar(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        temp = get_temp_folder(__file__, "temp_benchmark_progress_bar")

        params = [dict(value=random.randint(10, 20)) for i in range(0, 20)]

        bench = ATestBenchMarkB2_("TestName", clog=temp, fLOG=None,
                                  cache_file=os.path.join(
                                      temp, "cache.pickle"),
                                  progressbar=trange)
        bench.run(params)
        df = bench.to_df()
        ht = df.to_html(float_format="%1.3f", index=False)
        self.assertTrue(len(df) > 0)
        self.assertTrue(ht is not None)
        report = os.path.join(temp, "report.html")
        csv = os.path.join(temp, "report.csv")
        rst = os.path.join(temp, "report.rst")
        bench.report(filehtml=report, filecsv=csv, filerst=rst,
                     title="A Title", description="description")
        self.assertTrue(os.path.exists(report))
        self.assertTrue(os.path.exists(csv))
        self.assertTrue(os.path.exists(rst))


if __name__ == "__main__":
    unittest.main()
