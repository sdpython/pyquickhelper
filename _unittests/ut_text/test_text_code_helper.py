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

from src.pyquickhelper.texthelper import change_style, add_rst_links


class TestTextCodeHelper(unittest.TestCase):

    def test_src_import(self):
        """for pylint"""
        self.assertTrue(src is not None)

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


if __name__ == "__main__":
    unittest.main()
