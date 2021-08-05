# -*- coding: utf-8 -*-
"""
@brief      test tree node (time=1s)
"""
import unittest

from pyquickhelper.texthelper.text_diff import html_diffs


class TestTextDiff(unittest.TestCase):

    def test_text_diff(self):
        a = " a.b. c".replace(".", "\n")
        b = "a . c.d".replace(".", "\n")
        diff = html_diffs(a, b)
        self.assertIn("<div", diff)
        self.assertIn("</div", diff)
        lines = diff.split("\n")
        self.assertEqual(len(lines), 6)


if __name__ == "__main__":
    unittest.main()
