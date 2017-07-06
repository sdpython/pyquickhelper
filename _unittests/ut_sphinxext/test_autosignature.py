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

    def test_autosignature_html(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        this = os.path.abspath(os.path.dirname(__file__))
        data = os.path.join(this, "datadoc")
        sys.path.append(data)
        obj, name = import_object("exdocassert.onefunction", "function")

        newstring = ["AAAAAAAAAAAAAAAA",
                     ".. autosignature:: exdocassert.onefunction",
                     "BBBBBBBBBBBBBBBB",
                     ".. autofunction:: exdocassert.onefunction",
                     "CCCCCCCCCCCCCCCC"]
        newstring = "\n\n".join(newstring)
        htmls = rst2html(newstring, layout="sphinx_body")
        sys.path.pop()

        from docutils.parsers.rst.directives import _directives
        self.assertTrue("autosignature" in _directives)

        html = htmls.split("BBBBBBBBBBBBBBBB")
        if "onefunction" not in html[0]:
            raise Exception(html[0])
        if "onefunction" not in html[1]:
            raise Exception(html[1])

        if "<strong>a</strong>" not in html[1]:
            raise Exception(html[1])
        if "<strong>a</strong>" in html[0]:
            raise Exception(html[0])
        if ":param a:" in html[0]:
            raise Exception(html[0])
        if "`" in html[0]:
            raise Exception(html[0])
        if "if a and b have different types" in html[0]:
            raise Exception(html[0])
        if "Return the addition of" not in html[0]:
            raise Exception(html[0])

    def test_autosignature_class(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        this = os.path.abspath(os.path.dirname(__file__))
        data = os.path.join(this, "datadoc")
        sys.path.append(data)

        newstring = ["AAAAAAAAAAAAAAAA",
                     "",
                     ".. autosignature:: exsig.clex",
                     "    :members:",
                     "",
                     "CCCCCCCCCCCCCCCC"]
        newstring = "\n".join(newstring)
        htmls = rst2html(newstring, layout="sphinx_body")
        sys.path.pop()

        html = htmls.split("CCCCCCCCCCCCCCCC")
        if "onemethod" not in html[0]:
            raise Exception(html[0])
        if "<strong>a</strong>" in html[0]:
            raise Exception(html[0])
        if ":param a:" in html[0]:
            raise Exception(html[0])
        if "`" in html[0]:
            raise Exception(html[0])
        if "if a and b have different types" in html[0]:
            raise Exception(html[0])
        if "Return the addition of" not in html[0]:
            raise Exception(html[0])

    def test_autosignature_class_onemethod(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        this = os.path.abspath(os.path.dirname(__file__))
        data = os.path.join(this, "datadoc")
        sys.path.append(data)

        newstring = ["AAAAAAAAAAAAAAAA",
                     "",
                     ".. autosignature:: exsig.clex",
                     "    :members: onemethod",
                     "",
                     "CCCCCCCCCCCCCCCC"]
        newstring = "\n".join(newstring)
        htmls = rst2html(newstring, layout="sphinx_body")
        sys.path.pop()

        html = htmls.split("CCCCCCCCCCCCCCCC")
        if "onemethod" not in html[0]:
            raise Exception(html[0])
        if "<strong>a</strong>" in html[0]:
            raise Exception(html[0])
        if ":param a:" in html[0]:
            raise Exception(html[0])
        if "`" in html[0]:
            raise Exception(html[0])
        if "if a and b have different types" in html[0]:
            raise Exception(html[0])
        if "Return the addition of" not in html[0]:
            raise Exception(html[0])


if __name__ == "__main__":
    unittest.main()
