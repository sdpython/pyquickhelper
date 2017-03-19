"""
@brief      test log(time=2s)
@author     Xavier Dupre
"""

import sys
import os
import unittest
import random
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
from src.pyquickhelper.benchhelper import GridBenchMark


class TestOverGridBenchMark(GridBenchMark):

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

        bench = TestOverGridBenchMark("TestName", datasets, fLOG=fLOG, clog=temp,
                                      cache_file=os.path.join(temp, "cache.pickle"))
        bench.run(params)
        df = bench.to_df()
        ht = df.to_html(float_format="%1.3f", index=False)
        assert len(df) > 0
        assert ht
        self.assertEqual(df.shape[0], 4)
        report = os.path.join(temp, "report.html")
        csv = os.path.join(temp, "report.csv")
        rst = os.path.join(temp, "report.rst")
        bench.report(filehtml=report, filecsv=csv, filerst=rst,
                     title="A Title", description="description")
        assert os.path.exists(report)
        assert os.path.exists(csv)
        assert os.path.exists(rst)


if __name__ == "__main__":
    unittest.main()
