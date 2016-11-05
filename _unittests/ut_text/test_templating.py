# -*- coding: utf-8 -*-
"""
@brief      test tree node (time=1s)
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

from src.pyquickhelper.loghelper import fLOG
from src.pyquickhelper.texthelper.templating import apply_template, CustomTemplateException


class TestTemplating(unittest.TestCase):

    def test_mako(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        tmpl = """

            % for i in range(0, len(ll)):
                print(${ll[i]})
            % endfor
        """
        exp = """
                print(0)
                print(2)
            """
        res = apply_template(tmpl, dict(ll=[0, 2]))
        fLOG(res)
        self.assertEqual(res.replace(" ", "").replace("\n", ""),
                         exp.replace(" ", "").replace("\n", ""))

    def test_mako_exceptions(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        tmpl = """

            % for i in range(0, len(ll)):
                print(${ll[i]})
            % end for
        """
        exp = """
                print(0)
                print(2)
            """
        try:
            res = apply_template(tmpl, dict(ll=[0, 2]))
            assert False
        except CustomTemplateException as e:
            assert "0005" in str(e)
            return
        assert False
        fLOG(res)
        self.assertEqual(res.replace(" ", "").replace("\n", ""),
                         exp.replace(" ", "").replace("\n", ""))

    def test_mako_exceptions_not_here(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        tmpl = """

            % for i in range(0, len(lll)):
                print(${ll[i]})
            % endfor
        """
        exp = """
                print(0)
                print(2)
            """
        try:
            res = apply_template(tmpl, dict(lll=[0, 2]))
            assert False
        except CustomTemplateException as e:
            # fLOG(str(e))
            assert "Undefined" in str(e)
            return
        assert False
        fLOG(res)
        self.assertEqual(res.replace(" ", "").replace("\n", ""),
                         exp.replace(" ", "").replace("\n", ""))

    def test_jinja2(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        tmpl = """

            {% for i in range(0, len(ll)) %}
                print({{ll[i]}})
            {% endfor %}
        """
        exp = """
                print(0)
                print(2)
            """
        res = apply_template(tmpl, dict(ll=[0, 2], len=len), engine="jinja2")
        fLOG(res)
        self.assertEqual(res.replace(" ", "").replace("\n", ""),
                         exp.replace(" ", "").replace("\n", ""))

    def test_jinja2_exception(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        tmpl = """

            {% for i in range(0, len(ll)) %}
                print({{ll[i]}})
            {% end for %}
        """
        exp = """
                print(0)
                print(2)
            """
        try:
            res = apply_template(tmpl, dict(
                ll=[0, 2], len=len), engine="jinja2")
            assert False
        except CustomTemplateException as e:
            assert "0005" in str(e)
            return
        assert False
        fLOG(res)
        self.assertEqual(res.replace(" ", "").replace("\n", ""),
                         exp.replace(" ", "").replace("\n", ""))

    def test_jinja2_exception_not_here(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        tmpl = """

            {% for i in range(0, len(lll)) %}
                print({{ll[i]}})
            {% endfor %}
        """
        exp = """
                print(0)
                print(2)
            """
        try:
            res = apply_template(tmpl, dict(
                lll=[0, 2], len=len), engine="jinja2")
            assert False
        except CustomTemplateException as e:
            if "Some parameters are missing or mispelled" not in str(e):
                raise Exception(str(e))
            return
        assert False
        fLOG(res)
        self.assertEqual(res.replace(" ", "").replace("\n", ""),
                         exp.replace(" ", "").replace("\n", ""))


if __name__ == "__main__":
    unittest.main()
