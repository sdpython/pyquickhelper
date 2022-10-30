# -*- coding: utf-8 -*-
"""
@brief      test tree node (time=6s)
"""


import sys
import os
import unittest
import numpy
import pandas
import pyquickhelper
from pyquickhelper.sphinxext import sphinx_sharenet_extension
from pyquickhelper.texthelper import change_style, add_rst_links, code_helper
from pyquickhelper.texthelper.code_helper import (
    measure_documentation,
    measure_documentation_module)
from pyquickhelper import texthelper


class TestTextCodeHelper(unittest.TestCase):

    def test_change_style(self):
        self.assertEqual(change_style("changeStyle"), "change_style")
        self.assertEqual(change_style("change_Style"), "change__style")
        self.assertEqual(change_style("change_style"), "change_style")

    def test_add_rst_links(self):
        text = "Maybe... Python is winning the competition\nfor machine learning language$."
        values = {'Python': 'https://www.python.org/',
                  'machine learning': 'https://en.wikipedia.org/wiki/Machine_learning'}
        res = add_rst_links(text, values)
        exp = "Maybe... :epkg:`Python` is winning the competition\nfor :epkg:`machine learning` language$."
        self.assertEqual(exp, res)
        res = add_rst_links(res, values)
        self.assertEqual(exp, res)

    def test_measure_documentation(self):
        res = measure_documentation(code_helper, include_hidden=True,
                                    f_kind=lambda o: o.__name__)
        self.assertIn("function", res)
        c = res["function"]
        expected = {
            ("raw_length", "doc"): 0,
            ("raw_length", "code"): 0,
            ("length", "doc"): 0,
            ("length", "code"): 0,
            ("line", "doc"): 0,
            ("line", "code"): 0,
        }
        for k, v in expected.items():
            self.assertIn(k, c)
            self.assertGreater(c[k], v + 1)
        self.assertIn("measure_documentation", res)

    def test_measure_documentation_df(self):
        res = measure_documentation(
            code_helper, include_hidden=True, as_df=True)
        self.assertEqual(res.shape, (6, 4))
        self.assertEqual(list(res.columns), [
                         'kind', 'stat', 'doc_code', 'value'])

    def test_measure_documentation2(self):
        res = measure_documentation(sphinx_sharenet_extension, True)
        self.assertIn("function", res)
        c = res["function"]
        expected = {
            ("raw_length", "doc"): 0,
            ("raw_length", "code"): 0,
            ("length", "doc"): 0,
            ("length", "code"): 0,
            ("line", "doc"): 0,
            ("line", "code"): 0,
        }
        for k, v in expected.items():
            self.assertIn(k, c)
            self.assertGreater(c[k], v + 1)
        self.assertIn("class", res)
        c = res["class"]
        expected = {
            ("raw_length", "doc"): 0,
            ("raw_length", "code"): 0,
            ("length", "doc"): 0,
            ("length", "code"): 0,
            ("line", "doc"): 0,
            ("line", "code"): 0,
        }
        for k, v in expected.items():
            self.assertIn(k, c)
            self.assertGreater(c[k], v + 1)

    def test_measure_documentation3(self):
        res = measure_documentation_module(
            texthelper, True, f_kind=lambda o: o.__name__)
        self.assertIn("function", res)
        c = res["function"]
        expected = {
            ("raw_length", "doc"): 0,
            ("raw_length", "code"): 0,
            ("length", "doc"): 0,
            ("length", "code"): 0,
            ("line", "doc"): 0,
            ("line", "code"): 0,
        }
        for k, v in expected.items():
            self.assertIn(k, c)
            self.assertGreater(c[k], v + 1)

    def test_measure_documentation_mod(self):
        res = measure_documentation_module(pyquickhelper, True)
        self.assertIn("function", res)
        c = res["function"]
        expected = {
            ("raw_length", "doc"): 0,
            ("raw_length", "code"): 0,
            ("length", "doc"): 0,
            ("length", "code"): 0,
            ("line", "doc"): 0,
            ("line", "code"): 0,
        }
        for k, v in expected.items():
            self.assertIn(k, c)
            self.assertGreater(c[k], v + 1)

    def test_measure_documentation_numpy(self):
        res = measure_documentation_module([numpy, pandas], True, as_df=True)
        self.assertEqual(list(res.columns), [
                         'module', 'kind', 'stat', 'doc_code', 'value'])


if __name__ == "__main__":
    unittest.main(verbosity=2)
