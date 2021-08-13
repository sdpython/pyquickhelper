# -*- coding: utf-8 -*-
"""
@brief      test tree node (time=4s)
"""
import unittest
from textwrap import dedent
from pyquickhelper.pycode import ExtTestCase
from pyquickhelper.texthelper.edit_text_diff import (
    edit_distance_string, edit_distance_text, diff2html)
from pyquickhelper.texthelper.text_diff import html_diffs


class TestTextDiff(ExtTestCase):

    def test_text_diff(self):
        a = " a.b. c".replace(".", "\n")
        b = "a . c.d".replace(".", "\n")
        diff = html_diffs(a, b)
        self.assertIn("<div", diff)
        self.assertIn("</div", diff)
        lines = diff.split("\n")
        self.assertEqual(len(lines), 6)

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

    def test_edit_distance_text_big(self):
        f1 = dedent('''
            def edit_distance_string(s1, s2):
                """
                Computes the edit distance between strings *s1* and *s2*.

                :param s1: first string
                :param s2: second string
                :return: dist, list of tuples of aligned characters
                """
                n1 = len(s1) + 1
                n2 = len(s2) + 1
                dist = numpy.full((n1, n2), n1 * n2, dtype=numpy.float64)
                pred = numpy.full(dist.shape, 0, dtype=numpy.int32)

                for j in range(1, n2):
                    dist[0, j] = j
                    pred[0, j] = 2
                for i in range(0, n1):
                    dist[i, 0] = i
                    pred[i, 0] = 1
                pred[0, 0] = -1

                for j in range(1, n2):
                    for i in range(1, n1):
                        c = dist[i, j]

                        p = 0
                        if dist[i - 1, j] + 1 < c:
                            c = dist[i - 1, j] + 1
                            p = 1
                        if dist[i, j - 1] + 1 < c:
                            c = dist[i, j - 1] + 1
                            p = 2
                        d = 0 if s1[i - 1] == s2[j - 1] else 1
                        if dist[i - 1, j - 1] + d < c:
                            c = dist[i - 1, j - 1] + d
                            p = 3
                        if p == 0:
                            raise RuntimeError(
                                "Unexpected value for p=%d at position=%r." % (p, (i, j)))

                        dist[i, j] = c
                        pred[i, j] = p

                d = dist[len(s1), len(s2)]
                return d
            ''')

        f2 = dedent('''
            def edit_distance_string(s1, s2):
                """
                Computes the edit distance between strings *s1* and *s2*.

                :param s1: first string
                :param s2: second string
                :return: dist, list of tuples of aligned characters
                """
                n1 = len(s1) + 1
                n2 = len(s2) + 1
                dist = numpy.full((n1, n2), n1 * n2, dtype=numpy.float64)
                pred = numpy.full(dist.shape, 0, dtype=numpy.int32)

                for i in range(0, n1):
                    dist[i, 0] = i
                    pred[i, 0] = 1
                for j in range(1, n2):
                    dist[0, j] = j
                    pred[0, j] = 2
                pred[0, 0] = -1

                for i in range(1, n1):
                    for j in range(1, n2):
                        c = dist[i, j]

                        p = 0
                        if dist[i - 1, j] + 1 < c:
                            c = dist[i - 1, j] + 1
                            p = 1
                        if dist[i, j - 1] + 1 < c:
                            c = dist[i, j - 1] + 1
                            p = 2
                        d = 0 if s1[i - 1] == s2[j - 1] else 1
                        if dist[i - 1, j - 1] + d < c:
                            c = dist[i - 1, j - 1] + d
                            p = 3
                        if p == 0:
                            raise RuntimeError(
                                "Unexpected value for p=%d at position=%r." % (p, (i, j)))

                        dist[i, j] = c
                        pred[i, j] = p

                d = dist[len(s1), len(s2)]
                equals = []
                i, j = len(s1), len(s2)
                p = pred[i, j]
                while p != -1:
                    if p == 3:
                        equals.append((i - 1, j - 1))
                        i -= 1
                        j -= 1
                    elif p == 2:
                        j -= 1
                    elif p == 1:
                        i -= 1
                    else:
                        raise RuntimeError(
                            "Unexpected value for p=%d at position=%r." % (p, (i, j)))
                    p = pred[i, j]
                return d, list(reversed(equals))
            ''')
        d, aligned, final = edit_distance_text(f1, f2, verbose=False)
        self.assertGreater(d, 0)
        self.assertGreater(len(aligned), 10)
        self.assertIn((1, 1), final)


if __name__ == "__main__":
    # TestTextDiff().test_edit_distance_text_big()
    unittest.main()
