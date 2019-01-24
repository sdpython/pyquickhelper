"""
@brief      test log(time=8s)
@author     Xavier Dupre
"""

import sys
import os
import unittest
import pandas
import numpy


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

from src.pyquickhelper.pycode import ExtTestCase
from src.pyquickhelper.sphinxext.import_object_helper import import_object, import_any_object, import_path
from src.pyquickhelper.sphinxext.sphinx_autosignature import enumerate_extract_signature, enumerate_cleaned_signature
from src.pyquickhelper.helpgen import rst2html


def has_cpyquickhelper():
    try:
        import cpyquickhelper
        assert cpyquickhelper is not None
        return True
    except ImportError:
        return False


class TestAutoSignatureBug(ExtTestCase):

    @unittest.skipIf(not has_cpyquickhelper(), "cpyquickhelper not available")
    def test_import_object(self):
        obj = 'cpyquickhelper.numbers.cbenchmark.vector_dot_product16'
        res = import_object(obj, 'function', use_init=False)
        self.assertNotEmpty(res)
        res = import_any_object(obj)
        self.assertNotEmpty(res)

    @unittest.skipIf(not has_cpyquickhelper(), "cpyquickhelper not available")
    def test_autosignature_cplusplus(self):
        this = os.path.abspath(os.path.dirname(__file__))
        data = os.path.join(this, "datadoc")
        sys.path.append(data)
        from cpyquickhelper.numbers.cbenchmark import vector_dot_product16  # pylint: disable=E0611,E0401
        self.assertIn("Computes a dot product in C++",
                      vector_dot_product16.__doc__)

        newstring = ["AAAAAAAAAAAAAAAA",
                     "",
                     ".. autosignature:: cpyquickhelper.numbers.cbenchmark.vector_dot_product16",
                     "",
                     "CCCCCCCCCCCCCCCC"]
        newstring = "\n".join(newstring)
        text = rst2html(newstring, writer="rst")
        self.assertIn(
            "cpyquickhelper.numbers.cbenchmark.vector_dot_product16", text)
        self.assertIn("Computes a dot product in C++ with vectors", text)

    def test_signature(self):
        seg = 'vector_dot_product16(arg0: numpy.ndarray[float32], arg1: numpy.ndarray[float32]) -> float\n'
        res = enumerate_cleaned_signature(seg)
        r = list(res)
        self.assertIn("vector_dot_product16(arg0, arg1)", r)


if __name__ == "__main__":
    unittest.main()
