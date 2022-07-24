"""
@brief      test log(time=2s)
@author     Xavier Dupre
"""

import sys
import os
import unittest
import random

from pyquickhelper.loghelper import fLOG
from pyquickhelper.pycode import get_temp_folder
from pyquickhelper.benchhelper import BenchMark


class ATestBenchMark_(BenchMark):

    def init(self):
        pass

    def bench(self, **p):
        h = random.randint(1, 100)
        return dict(nb=h, value=p["value"], _btry=str(h)), dict(nb=h, script="a\nb", _btry=str(h))

    def end(self):
        pass


class ATestBenchMark2_(BenchMark):

    def init(self):
        pass

    def bench(self, **p):
        h = random.randint(1, 100)
        return [(dict(nb=h, value=p["value"], _btry=str(h)), dict(nb=h, script="a\nb", _btry=str(h)))]

    def end(self):
        pass


class TestBenchMark(unittest.TestCase):

    def test_benchmark(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        temp = get_temp_folder(__file__, "temp_benchmark")

        local_graph = BenchMark.LocalGraph(lambda ax: ax, filename=os.path.join(
            temp, "zzz/g.png"), title="agraph", root=temp)
        local_graph.add("alt", "h")
        link = local_graph.to_html()
        self.assertEqual(link, '<img src="zzz/g.png" alt="agraph"/>')
        rst = local_graph.to_rst()
        self.assertEqual(rst, '.. image:: zzz/g.png')

        params = [dict(value=random.randint(10, 20)) for i in range(0, 20)]

        bench = ATestBenchMark_("TestName", fLOG=fLOG, clog=temp,
                                cache_file=os.path.join(temp, "cache.pickle"))
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
        df1 = bench.to_df()

        # second run

        fLOG("NEW RUN")
        bench = ATestBenchMark_("TestName", fLOG=fLOG, clog=temp,
                                cache_file=os.path.join(temp, "cache.pickle"))
        bench.run(params)
        meta = bench.Metadata
        fLOG(meta)
        if sys.version_info[0] >= 3:
            self.assertEqual(meta[0]["nb_cached"], 20)
        df2 = bench.to_df()
        self.assertEqual(df1.shape, df2.shape)

        # clear one cache
        name = bench._metrics[0]["_btry"]
        look = os.path.join(temp, f"cache.pickle.{name}.clean_cache")
        if not os.path.exists(look):
            raise FileNotFoundError(look)
        os.remove(look)

        # third run

        fLOG("NEW RUN")
        bench = ATestBenchMark_("TestName", fLOG=fLOG, clog=temp,
                                cache_file=os.path.join(temp, "cache.pickle"))
        bench.run(params)
        meta = bench.Metadata
        fLOG(meta)
        self.assertTrue(meta[0]["nb_cached"] < 20)
        df2 = bench.to_df()
        self.assertEqual(df1.shape, df2.shape)


if __name__ == "__main__":
    unittest.main()
