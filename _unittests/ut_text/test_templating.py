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
from src.pyquickhelper.texthelper.templating import apply_template


class TestTemplating(unittest.TestCase):

    def test_mako(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        tmpl = """

            % for i in range(0, len(l)):
                print(${l[i]})
            % endfor
        """
        exp = """
                print(0)
                print(2)
            """
        res = apply_template(tmpl, dict(l=[0, 2]))
        fLOG(res)
        self.assertEqual(res.replace(" ", "").replace("\n", ""),
                         exp.replace(" ", "").replace("\n", ""))

    def test_jinja2(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        tmpl = """

            {% for i in range(0, len(l)) %}
                print({{l[i]}})
            {% endfor %}
        """
        exp = """
                print(0)
                print(2)
            """
        res = apply_template(tmpl, dict(l=[0, 2], len=len), engine="jinja2")
        fLOG(res)
        self.assertEqual(res.replace(" ", "").replace("\n", ""),
                         exp.replace(" ", "").replace("\n", ""))


if __name__ == "__main__":
    unittest.main()
