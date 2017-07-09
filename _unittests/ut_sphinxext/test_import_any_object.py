"""
@brief      test log(time=8s)
@author     Xavier Dupre
"""

import sys
import os
import unittest


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

from src.pyquickhelper.loghelper.flog import fLOG
from src.pyquickhelper.sphinxext.import_object_helper import import_any_object


class TestImportAnyObject(unittest.TestCase):

    def test_import_any_object(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        this = os.path.abspath(os.path.dirname(__file__))
        data = os.path.join(this, "datadoc")
        sys.path.append(data)
        obj, name, kind = import_any_object("exsig.clex")
        sys.path.pop()
        self.assertTrue(obj is not None)
        # self.assertTrue(obj.(4, 5), 9)
        self.assertEqual(name, "clex")
        self.assertEqual(kind, "class")

    def test_import_any_object_benchmark(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        this = os.path.abspath(os.path.dirname(__file__))
        data = os.path.join(this, "datadoc")
        sys.path.append(data)
        name = "src.pyquickhelper.benchhelper.grid_benchmark.GridBenchMark.bench_experiment"
        obj, name, kind = import_any_object(name)
        sys.path.pop()
        self.assertTrue(obj is not None)
        # self.assertTrue(obj.(4, 5), 9)
        self.assertEqual(name, "bench_experiment")
        self.assertEqual(kind, "method")


if __name__ == "__main__":
    unittest.main()
