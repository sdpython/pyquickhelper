"""
@brief      test log(time=8s)
@author     Xavier Dupre
"""
import os
import unittest
import logging
import pandas
import numpy
from pyquickhelper.loghelper import sys_path_append
from pyquickhelper.pycode import ExtTestCase
from pyquickhelper.sphinxext.import_object_helper import (
    import_object, import_any_object, import_path)
from pyquickhelper.sphinxext.sphinx_autosignature import (
    enumerate_extract_signature, enumerate_cleaned_signature)
from pyquickhelper.helpgen import rst2html


class TestAutoSignature(ExtTestCase):

    def test_import_object(self):
        this = os.path.abspath(os.path.dirname(__file__))
        data = os.path.join(this, "datadoc")
        with sys_path_append(data):
            obj, name = import_object("exdocassert.onefunction", "function")
            self.assertTrue(obj is not None)
            self.assertTrue(obj(4, 5), 9)

    def test_import_object_any(self):
        this = os.path.abspath(os.path.dirname(__file__))
        data = os.path.join(this, "datadoc")
        with sys_path_append(data):
            obj, name, kind = import_any_object("exdocassert.onefunction")
            self.assertTrue(obj is not None)
            self.assertTrue(obj(4, 5), 9)
            self.assertEqual(kind, 'function')

    def test_import_object_kind_check(self):
        self.assertNotEmpty(import_object('pandas.DataFrame', 'class'))
        self.assertRaise(lambda: import_object(
            'pandas.DataFrame', 'function'), TypeError)
        self.assertNotEmpty(import_object(
            'pandas.core.frame.DataFrame', 'class'))
        self.assertRaise(lambda: import_object(
            'pandas.core.frame.DataFrame', 'function'), TypeError)
        obj, name, kind = import_any_object("pandas.core.frame.DataFrame")
        self.assertNotEmpty(obj)
        self.assertEqual(name, 'DataFrame')
        self.assertEqual(kind, 'class')

    def test_import_path(self):
        ipath = import_path(pandas.DataFrame)
        self.assertEqual(ipath, 'pandas')
        ipath = import_path(rst2html)
        self.assertIn(ipath, ('pyquickhelper.helpgen', ))

    def test_import_path_loc(self):
        this = os.path.abspath(os.path.dirname(__file__))
        data = os.path.join(this, "datadoc")
        with sys_path_append(data):
            from exsig import clex
            ipath = import_path(clex)
            self.assertEqual(ipath, 'exsig')

    def test_autosignature_html(self):
        this = os.path.abspath(os.path.dirname(__file__))
        data = os.path.join(this, "datadoc")
        with sys_path_append(data):
            obj, name = import_object("exdocassert.onefunction", "function")

            newstring = ["AAAAAAAAAAAAAAAA",
                         ".. autosignature:: exdocassert.onefunction",
                         "BBBBBBBBBBBBBBBB",
                         ".. autofunction:: exdocassert.onefunction",
                         "CCCCCCCCCCCCCCCC"]
            newstring = "\n\n".join(newstring)
            htmls = rst2html(newstring, layout="sphinx_body")

        self.assertIn("CCCCCCCCCCCCCCCC", htmls)

        from docutils.parsers.rst.directives import _directives
        self.assertTrue("autosignature" in _directives)

        html = htmls.split("BBBBBBBBBBBBBBBB")
        self.assertIn("onefunction", html[0])
        self.assertIn("onefunction", html[1])
        self.assertIn("<strong>a</strong>", html[1])
        self.assertNotIn("<strong>a</strong>", html[0])
        self.assertNotIn(":param a:", html[0])
        self.assertNotIn("`", html[0])
        self.assertNotIn("if a and b have different types", html[0])
        self.assertIn("Return the addition of", html[0])

    def test_autosignature_class(self):
        this = os.path.abspath(os.path.dirname(__file__))
        data = os.path.join(this, "datadoc")
        with sys_path_append(data):
            newstring = ["AAAAAAAAAAAAAAAA",
                         "",
                         ".. autosignature:: exsig.clex",
                         "    :members:",
                         "",
                         "CCCCCCCCCCCCCCCC"]
            newstring = "\n".join(newstring)
            htmls = rst2html(newstring, layout="sphinx_body")

        self.assertIn("CCCCCCCCCCCCCCCC", htmls)

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
        this = os.path.abspath(os.path.dirname(__file__))
        data = os.path.join(this, "datadoc")
        with sys_path_append(data, 0):
            newstring = ["AAAAAAAAAAAAAAAA",
                         "",
                         ".. autosignature:: exsig.clex",
                         "    :members: onemethod",
                         "",
                         "CCCCCCCCCCCCCCCC"]
            newstring = "\n".join(newstring)
            htmls = rst2html(newstring, layout="sphinx_body")

        self.assertIn("CCCCCCCCCCCCCCCC", htmls)

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

    def test_autosignature_class_onemethod2(self):
        this = os.path.abspath(os.path.dirname(__file__))
        data = os.path.join(this, "datadoc")
        with sys_path_append(data):

            newstring = ["AAAAAAAAAAAAAAAA",
                         "",
                         ".. autosignature:: exdocassert2.onefunction",
                         "",
                         "CCCCCCCCCCCCCCCC"]
            newstring = "\n".join(newstring)
            htmls = rst2html(newstring, layout="sphinx_body")

        self.assertIn("CCCCCCCCCCCCCCCC", htmls)

        html = htmls.split("CCCCCCCCCCCCCCCC")
        if "onefunction" not in html[0]:
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
        if "Second line should be aligned." not in html[0]:
            raise Exception(html[0])
        if "<p>Return the addition of" not in html[0]:
            raise Exception(html[0])
        if "should be aligned.</p>" not in html[0]:
            raise Exception(html[0])

    def test_autosignature_class_static_method(self):
        this = os.path.abspath(os.path.dirname(__file__))
        data = os.path.join(this, "datadoc")
        with sys_path_append(data):

            obj = import_object("exsig.clex.static_method", "staticmethod")
            self.assertTrue(obj is not None)

            newstring = ["AAAAAAAAAAAAAAAA",
                         "",
                         ".. autosignature:: exsig.clex.static_method",
                         "",
                         "CCCCCCCCCCCCCCCC"]
            newstring = "\n".join(newstring)
            htmls = rst2html(newstring, layout="sphinx_body")

        self.assertIn("CCCCCCCCCCCCCCCC", htmls)

        html = htmls.split("CCCCCCCCCCCCCCCC")
        if "static_method" not in html[0]:
            raise Exception(html[0])
        if "<strong>a</strong>" in html[0]:
            raise Exception(html[0])
        if ":param a:" in html[0]:
            raise Exception(html[0])
        if "`" in html[0]:
            raise Exception(html[0])
        if "if a and b have different types" in html[0]:
            raise Exception(html[0])
        if "Return the static addition of" not in html[0]:
            raise Exception(html[0])
        if "<p>Return the static addition of" not in html[0]:
            raise Exception(html[0])

    def test_autosignature_path_option(self):
        newstring = [".. autosignature:: pandas.core.frame.DataFrame",
                     "    :path: name"]
        newstring = "\n".join(newstring)
        res = rst2html(newstring, writer="rst", layout="sphinx")
        self.assertIn(
            ':py:class:`DataFrame <pandas.core.frame.DataFrame>', res)
        self.assertNotIn(
            ':py:class:`pandas.DataFrame <pandas.core.frame.DataFrame>', res)
        self.assertNotIn(
            ':py:class:`pandas.core.frame.DataFrame', res)

        newstring = [".. autosignature:: pandas.core.frame.DataFrame",
                     "    :path: full"]
        newstring = "\n".join(newstring)
        res = rst2html(newstring, writer="rst", layout="sphinx")
        self.assertNotIn('`DataFrame <pandas.core', res)
        self.assertNotIn('`pandas.DataFrame <pandas.core', res)

        newstring = [".. autosignature:: pandas.core.frame.DataFrame"]
        newstring = "\n".join(newstring)
        res = rst2html(newstring, writer="rst", layout="sphinx")
        self.assertIn(
            ':py:class:`pandas.DataFrame <pandas.core.frame.DataFrame>` (*self*', res)

    def test_autosignature_open(self):
        self.assertIsInstance(numpy.ndarray.__init__.__text_signature__, str)
        res = import_object("numpy.ndarray.__init__", "method")
        self.assertNotEmpty(res)
        obj, _, kind = import_any_object(
            "numpy.ndarray.__init__", use_init=False)
        self.assertNotEmpty(obj)
        self.assertIn(kind, ("method", "property"))
        newstring = [
            ".. autosignature:: numpy.ndarray.__init__\n    :path: full"]
        newstring = "\n".join(newstring)
        res = rst2html(newstring, writer="rst", layout="sphinx")
        self.assertIn("numpy.ndarray.__init__", res)

    def test_extract_signature(self):
        sigs = ["__init__(self: cpyquickhelper.numbers.weighted_number.WeightedDouble, value: float, weight: float=1.0) -> None",
                "__init__()",
                "__init__(a)",
                "__init__(a=1)",
                "__init__(a, b)",
                "__init__(a, b=1)",
                "__init__(a, b=1, c:int=2)",
                ]
        exps = ["__init__(self, value, weight=1.0)",
                "__init__()",
                "__init__(a)",
                "__init__(a=1)",
                "__init__(a, b)",
                "__init__(a, b=1)",
                "__init__(a, b=1, c=2)",
                ]

        for sig, exp in zip(sigs, exps):
            res = list(enumerate_extract_signature(sig))
            for r in res:
                g = r.groupdict()
                self.assertNotEmpty(g)

            res = list(enumerate_cleaned_signature(sig))
            self.assertEqual(len(res), 1)
            self.assertEqual(res[0], exp)

    def test_autosignature_class_onemethod2_debug(self):
        this = os.path.abspath(os.path.dirname(__file__))
        data = os.path.join(this, "datadoc")
        with sys_path_append(data):

            newstring = ["AAAAAAAAAAAAAAAA",
                         "",
                         ".. autosignature:: exdocassert2.onefunction",
                         "    :debug:",
                         "    :syspath: aaa;bbbb",
                         "",
                         "CCCCCCCCCCCCCCCC"]
            newstring = "\n".join(newstring)
            htmls = rst2html(newstring, writer="rst")

        self.assertIn('[debug]', htmls)
        self.assertIn('[import_any_object]', htmls)

    def test_autosignature_issue(self):
        newstring = ["AAAAAAAAAAAAAAAA",
                     ".. autosignature:: exdocassert2222",
                     "CCCCCCCCCCCCCCCC"]
        newstring = "\n\n".join(newstring)
        res, logs = self.assertLogging(
            lambda: rst2html(newstring, writer='rst', layout="sphinx"),
            'autosignature', log_sphinx=True)
        self.assertIn("CCCCCCCCCCCCCCCC", res)
        self.assertIn(
            "[autosignature] object 'exdocassert2222' cannot be imported.", logs)

    def test_autosignature_empty_variable(self):
        newstring = ["AAAAAAAAAAAAAAAA",
                     ".. autosignature:: variable.empty_variable",
                     "CCCCCCCCCCCCCCCC"]
        newstring = "\n\n".join(newstring)
        this = os.path.abspath(os.path.dirname(__file__))
        data = os.path.join(this, "datadoc")
        with sys_path_append(data):
            res, logs = self.assertLogging(
                lambda: rst2html(newstring, writer='rst', layout="sphinx"),
                'autosignature', log_sphinx=True)
            self.assertIn("CCCCCCCCCCCCCCCC", res)
            self.assertIn("unable to import 'variable.empty_variable'", logs)
            self.assertIn("TypeError", logs)


if __name__ == "__main__":
    unittest.main()
