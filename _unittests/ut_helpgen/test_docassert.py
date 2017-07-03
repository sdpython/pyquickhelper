"""
@brief      test log(time=8s)
@author     Xavier Dupre
"""

import sys
import os
import unittest
import warnings


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
from src.pyquickhelper.sphinxext.sphinx_docassert_extension import import_object
from src.pyquickhelper.helpgen import rst2html


class TestDocAssert(unittest.TestCase):

    def test_import_object(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        this = os.path.abspath(os.path.dirname(__file__))
        data = os.path.join(this, "datadoc")
        sys.path.append(data)
        obj, name = import_object("exdocassert.onefunction", "function")
        self.assertTrue(obj is not None)
        self.assertTrue(obj(4, 5), 9)
        sys.path.pop()

    def test_docassert_html(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        this = os.path.abspath(os.path.dirname(__file__))
        data = os.path.join(this, "datadoc")
        sys.path.append(data)
        obj, name = import_object("exdocassert.onefunction", "function")
        docstring = obj.__doc__
        with warnings.catch_warnings(record=True) as ws:
            html = rst2html(docstring)
            if "if a and b have different" not in html:
                raise Exception(html)
            fLOG(len(ws))

        newstring = ".. autofunction:: exdocassert.onefunction"
        with warnings.catch_warnings(record=True) as ws:
            html = rst2html(newstring)
            fLOG("number of warnings", len(ws))
            for i, w in enumerate(ws):
                fLOG(i, ":", w)
            if "if a and b have different" not in html:
                html = rst2html(newstring, fLOG=fLOG)
                fLOG("number of warnings", len(ws))
                for i, w in enumerate(ws):
                    fLOG(i, ":", str(w).replace("\\n", "\n"))
                raise Exception(html)

        from docutils.parsers.rst.directives import _directives
        self.assertTrue("autofunction" in _directives)

        fLOG(html)
        sys.path.pop()


if __name__ == "__main__":
    unittest.main()
