# -*- coding: utf-8 -*-
"""
@brief      test tree node (time=1s)
"""
import unittest
from pyquickhelper.pycode import ExtTestCase
from pyquickhelper.texthelper.edit_text_diff import (
    edit_distance_string, edit_distance_text, diff2html)


class TestTextDiff(ExtTestCase):

    def test_edit_distance_string(self):
        s1 = "ABCD"
        s2 = "ACD"
        d, aligned = edit_distance_string(s1, s2)
        self.assertEqual(d, 1)
        self.assertEqual(aligned, [(0, 0), (2, 1), (3, 2)])
        d, aligned = edit_distance_string(s2, s1)
        self.assertEqual(d, 1)
        self.assertEqual(aligned, [(0, 0), (1, 2), (2, 3)])

    def test_edit_distance_string_empty(self):
        s1 = ""
        s2 = "ACD"
        d, aligned = edit_distance_string(s1, s2)
        self.assertEqual(d, 3)
        self.assertEqual(aligned, [])
        s1 = "ABCD"
        s2 = ""
        d, aligned = edit_distance_string(s1, s2)
        self.assertEqual(d, 4)
        self.assertEqual(aligned, [])

    def test_edit_distance_text(self):
        s1 = "AA\nBB\nCC\nDD"
        s2 = "AA\nCC\nDD"
        d, aligned, final = edit_distance_text(s1, s2)
        self.assertEqual(len(aligned), 3)
        self.assertEqual(d, 0.98)
        self.assertEqual(aligned, [(0, 0, 0.0, [(0, 0), (1, 1)]),
                                   (2, 1, 0.0, [(0, 0), (1, 1)]),
                                   (3, 2, 0.0, [(0, 0), (1, 1)])])
        self.assertEqual(final, [(0, 0), (1, None), (2, 1), (3, 2)])
        d, aligned, final = edit_distance_text(s2, s1)
        self.assertEqual(len(aligned), 3)
        self.assertEqual(d, 0.98)
        self.assertEqual(aligned, [(0, 0, 0.0, [(0, 0), (1, 1)]),
                                   (1, 2, 0.0, [(0, 0), (1, 1)]),
                                   (2, 3, 0.0, [(0, 0), (1, 1)])])
        self.assertEqual(final, [(0, 0), (None, 1), (1, 2), (2, 3)])

    def test_edit_distance_html(self):
        s1 = "AA\nBB\nCC\nZZZZZA\nDD"
        s2 = "AA\nCC\nDD\nZZZZZB\nEE"
        _, aligned, final = edit_distance_text(s1, s2)
        ht = diff2html(s1, s2, aligned, final)
        self.assertIn(
            '<tr style="1px solid black;"><td>2</td><td>1</td><td>CC</td></tr>', ht)
        self.assertIn('<td style="background-color:#ABEBC6;">', ht)
        self.assertIn('<td style="background-color:#E5E7E9;">', ht)

    def test_edit_distance_text_empty(self):
        s1 = "AA\nBB\nCC\nDD"
        s2 = ""
        d, aligned, final = edit_distance_text(s1, s2)
        self.assertEqual(len(aligned), 0)
        self.assertEqual(d, 0.98)
        self.assertEqual(aligned, [])
        self.assertEqual(
            final, [(0, None), (1, None), (2, None), (3, None), (None, 0)])

    def test_edit_distance_text_empty2(self):
        s1 = ""
        s2 = "AA\nCC\nDD"
        d, aligned, final = edit_distance_text(s1, s2)
        self.assertEqual(len(aligned), 0)
        self.assertEqual(d, 0.98)
        self.assertEqual(aligned, [])
        self.assertEqual(final, [(0, None), (None, 0), (None, 1), (None, 2)])


if __name__ == "__main__":
    # TestTextDiff().test_edit_distance_text()
    unittest.main()
