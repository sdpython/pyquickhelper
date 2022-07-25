"""
@brief      test log(time=8s)
@author     Xavier Dupre
"""
import sys
import os
import unittest
from pyquickhelper.sphinxext.import_object_helper import (
    import_any_object, import_object)
from pyquickhelper.pycode import ExtTestCase
from pyquickhelper.loghelper import sys_path_append


class TestImportAnyObject(ExtTestCase):

    def test_import_any_object(self):
        this = os.path.abspath(os.path.dirname(__file__))
        data = os.path.join(this, "datadoc")
        with sys_path_append(data):
            obj, name, kind = import_any_object("exsig.clex")
        self.assertTrue(obj is not None)
        # self.assertTrue(obj.(4, 5), 9)
        self.assertEqual(name, "clex")
        self.assertEqual(kind, "class")

    def test_import_any_object_benchmark(self):
        this = os.path.abspath(os.path.dirname(__file__))
        data = os.path.join(this, "datadoc")
        with sys_path_append(data):
            name = "pyquickhelper.benchhelper.grid_benchmark.GridBenchMark.bench_experiment"
            import_object(name, "method")
            obj, name, kind = import_any_object(name)
        self.assertTrue(obj is not None)
        # self.assertTrue(obj.(4, 5), 9)
        self.assertEqual(name, "bench_experiment")
        self.assertEqual(kind, "method")

    def test_import_any_object_static(self):
        this = os.path.abspath(os.path.dirname(__file__))
        data = os.path.join(this, "datadoc")
        with sys_path_append(data):
            name = "pyquickhelper.filehelper.transfer_api.TransferAPI_FileInfo.read_json"
            try:
                import_object(name, "method")
                self.assertTrue(False)
            except TypeError as e:
                pass
            import_object(name, "staticmethod")
            obj, name, kind = import_any_object(name)
        self.assertTrue(obj is not None)
        # self.assertTrue(obj.(4, 5), 9)
        self.assertEqual(name, "read_json")
        self.assertEqual(kind, "staticmethod")

    def test_import_any_object_property(self):
        this = os.path.abspath(os.path.dirname(__file__))
        data = os.path.join(this, "datadoc")
        sys.path.append(data)
        name = "pyquickhelper.benchhelper.benchmark.BenchMark.Name"
        import_object(name, "property")

        obj, name, kind = import_any_object(name)
        sys.path.pop()
        self.assertTrue(obj is not None)
        # self.assertTrue(obj.(4, 5), 9)
        self.assertEqual(name, "Name")
        self.assertEqual(kind, "property")


if __name__ == "__main__":
    unittest.main()
