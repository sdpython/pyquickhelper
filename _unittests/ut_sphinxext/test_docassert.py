"""
@brief      test log(time=8s)
@author     Xavier Dupre
"""
import sys
import os
import unittest
import warnings
import logging
from io import StringIO

from pyquickhelper.loghelper.flog import fLOG
from pyquickhelper.sphinxext.import_object_helper import import_object
from pyquickhelper.helpgen import rst2html
from sphinx.util.logging import getLogger


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

        logger1 = getLogger("MockSphinxApp")
        logger2 = getLogger("docassert")

        log_capture_string = StringIO()
        ch = logging.StreamHandler(log_capture_string)
        ch.setLevel(logging.DEBUG)
        logger1.logger.addHandler(ch)
        logger2.logger.addHandler(ch)

        this = os.path.abspath(os.path.dirname(__file__))
        data = os.path.join(this, "datadoc")
        sys.path.append(data)
        obj, name = import_object("exdocassert.onefunction", "function")
        docstring = obj.__doc__
        with warnings.catch_warnings(record=True) as ws:
            html = rst2html(docstring)
            if "if a and b have different" not in html:
                raise Exception(html)

        newstring = ".. autofunction:: exdocassert.onefunction"
        with warnings.catch_warnings(record=True) as ws:
            html = rst2html(newstring)
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

        sys.path.pop()

        lines = log_capture_string.getvalue().split("\n")
        if len(lines) > 0:
            for line in lines:
                if "'onefunction' has no parameter 'TypeError'" in line:
                    raise Exception(
                        "This warning should not happen.\n{0}".format("\n".join(lines)))
        self.assertTrue("<strong>a</strong>" in html)

    def test_docassert_html_bug(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        class MyStream:
            def __init__(self):
                self.rows = []

            def write(self, text):
                fLOG(
                    "[warning*] {0} - '{1}'".format(len(self), text.strip("\n\r ")))
                self.rows.append(text)

            def getvalue(self):
                return "\n".join(self.rows)

            def __len__(self):
                return len(self.rows)

        logger1 = getLogger("MockSphinxApp")
        logger2 = getLogger("docassert")
        log_capture_string = MyStream()  # StringIO()
        ch = logging.StreamHandler(log_capture_string)
        ch.setLevel(logging.DEBUG)
        logger1.logger.addHandler(ch)
        logger2.logger.addHandler(ch)
        logger2.warning("try")

        this = os.path.abspath(os.path.dirname(__file__))
        data = os.path.join(this, "datadoc")
        sys.path.append(data)
        obj, name = import_object("exdocassert2.onefunction", "function")
        newstring = ".. autofunction:: exdocassert2.onefunction"
        html = rst2html(newstring)
        self.assertTrue(html is not None)
        sys.path.pop()
        fLOG(len(log_capture_string))

        lines = log_capture_string.getvalue().split("\n")
        if len(lines) == 0:
            raise Exception("no warning")
        nb = 0
        for line in lines:
            if "'onefunction' has no parameter 'c'" in line:
                nb += 1
        if nb == 0:
            raise Exception("not the right warning")

    def test_docassert_html_method(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        class MyStream:
            def __init__(self):
                self.rows = []

            def write(self, text):
                fLOG(
                    "[warning*] {0} - '{1}'".format(len(self), text.strip("\n\r ")))
                self.rows.append(text)

            def getvalue(self):
                return "\n".join(self.rows)

            def __len__(self):
                return len(self.rows)

        logger1 = getLogger("MockSphinxApp")
        logger2 = getLogger("docassert")
        log_capture_string = MyStream()  # StringIO()
        ch = logging.StreamHandler(log_capture_string)
        ch.setLevel(logging.DEBUG)
        logger1.logger.addHandler(ch)
        logger2.logger.addHandler(ch)
        logger2.warning("try")

        this = os.path.abspath(os.path.dirname(__file__))
        data = os.path.join(this, "datadoc")
        sys.path.append(data)
        obj, name = import_object("exsig.clex.onemethod", "method")
        newstring = ".. automethod:: exsig.clex.onemethod"
        html = rst2html(newstring)
        self.assertTrue(html is not None)
        sys.path.pop()
        fLOG(len(log_capture_string))

        lines = log_capture_string.getvalue().split("\n")
        if len(lines) == 0:
            raise Exception("no warning")
        nb = 0
        for line in lines:
            if "'onemethod' has no parameter 'c'" in line:
                nb += 1
        if nb == 0:
            raise Exception("not the right warning")
        for line in lines:
            if "'onemethod' has undocumented parameters 'b, self'" in line:
                raise Exception(line)


if __name__ == "__main__":
    unittest.main()
