"""
@brief      test log(time=2s)
@author     Xavier Dupre
"""

import sys
import os
import unittest
import random
import pandas

from pyquickhelper.loghelper import fLOG
from pyquickhelper.pycode import get_temp_folder
from pyquickhelper.benchhelper import GridBenchMark


class ATestOverGridBenchMark(GridBenchMark):

    def init(self):
        pass

    def bench_experiment(self, info, **params):
        return {"mtrain": 0.4}

    def end(self):
        pass

    def predict_score_experiment(self, info, output, **params):
        return dict(score=0.5), dict()


class TestGridBenchMark(unittest.TestCase):

    def test_benchmark(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        temp = get_temp_folder(__file__, "temp_grid_benchmark")

        params = [dict(value=random.randint(10, 20), name="name%d" %
                       i, shortname="m%d" % i) for i in range(0, 2)]
        datasets = [dict(X=pandas.DataFrame([[0, 1], [0, 1]]), name="set1", shortname="s1"),
                    dict(X=pandas.DataFrame([[1, 1], [1, 1]]), name="set2", shortname="s2"), ]

        bench = ATestOverGridBenchMark("TestName", datasets, fLOG=fLOG, clog=temp,
                                       cache_file=os.path.join(temp, "cache.pickle"))
        bench.run(params)
        df = bench.to_df()
        ht = df.to_html(float_format="%1.3f", index=False)
        self.assertTrue(len(df) > 0)
        self.assertTrue(ht is not None)
        self.assertEqual(df.shape[0], 4)
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
