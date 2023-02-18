"""
@brief      test log(time=1s)
@author     Xavier Dupre
"""


import sys
import os
import unittest

import pyquickhelper.helpgen.utils_sphinx_doc as utils_sphinx_doc
from pyquickhelper.loghelper import fLOG
from pyquickhelper.pycode import ExtTestCase


class TestSphinxDoc2(ExtTestCase):

    def test_apply_modification_template_obj(self):
        path = os.path.split(__file__)[0]
        file = os.path.normpath(
            os.path.join(
                path,
                "..",
                "..",
                "src",
                "pyquickhelper",
                "loghelper",
                "pqh_exception.py"))
        rootm = os.path.normpath(os.path.join(path, "..", "..", "src"))
        rootrep = ("pyquickhelper.src.pyquickhelper.", "")
        store_obj = {}

        def softfile(f):
            return False

        rst = utils_sphinx_doc.apply_modification_template(rootm, store_obj,
                                                           utils_sphinx_doc.add_file_rst_template,
                                                           file, rootrep, softfile,
                                                           {}, additional_sys_path=[],
                                                           fLOG=fLOG)

        self.assertNotEmpty(rst)
        self.assertNotEmpty(store_obj)
        for k, v in store_obj.items():
            fLOG("test1", k, v)

    @staticmethod
    def private_static():
        """ doc pr"""
        res = 0
        return res

    @property
    def prop(self):
        """ doc prop"""
        return 1

    def __gt__(self, o):
        """doc gt"""
        return True

    def test_inspect_object(self):
        """ test 2"""
        mod = sys.modules[__name__]
        objs = utils_sphinx_doc.get_module_objects(mod)
        ty = {}
        for _ in objs:
            ty[_.type] = ty.get(_.type, 0) + 1
        if ty.get("method", 0) > 5 or ty.get("staticmethod", 0) == 0:
            for _ in objs:
                if _.type == "method":
                    continue
                if "private" in _.name:
                    self.assertIn("doc pr", _.doc)
                fLOG(_.type, _.name, _.doc.replace("\n", "\\n"))
            for _ in objs:
                if _.type != "method":
                    continue
                fLOG(_.type, _.module, _.name, _.doc.replace("\n", "\\n"))

        self.assertEqual(ty.get("property", 0), 1)
        if ty.get("staticmethod", 0) != 1:
            raise AssertionError(f"{str(ty)}")
        self.assertGreater(ty["method"], 1)


if __name__ == "__main__":
    unittest.main()
