"""
@brief      test log(time=2s)
"""
import unittest
import warnings

from pyquickhelper.pycode import ExtTestCase
from pyquickhelper.ipythonhelper.magic_class_diff import MagicDiff


class TestMagicDiff(ExtTestCase):

    def test_textdiff(self):
        from IPython.core.display import Javascript
        mg = MagicDiff()
        mg.add_context(
            {"f1": "STRING1\nSTRING2", "f2": "STRING1\nSTRING3"})
        cmd = "f1 f2"
        res = self.capture(lambda: mg.textdiff(cmd))[0]
        self.assertIsInstance(res, Javascript)

    def test_strdiff(self):
        from IPython.core.display import HTML
        mg = MagicDiff()
        mg.add_context(
            {"f1": "STRING1\nSTRING2", "f2": "STRING1\nSTRING3"})
        cmd = "f1 f2"
        res = mg.strdiff(cmd)
        self.assertIsInstance(res, HTML)

    def test_codediff(self):
        from IPython.core.display import HTML
        mg = MagicDiff()
        mg.add_context(
            {"f1": "STRING1\nSTRING2", "f2": "STRING1\nSTRING3"})
        cmd = "f1 f2"
        res = mg.codediff(cmd)
        self.assertIsInstance(res, HTML)

    def test_codediff_two(self):
        from IPython.core.display import HTML
        mg = MagicDiff()
        mg.add_context(
            {"f1": "STRING1\nSTRING2", "f2": "STRING1\nSTRING3"})
        cmd = "f1 f2 --two 1"
        res = mg.codediff(cmd)
        self.assertIsInstance(res, HTML)


if __name__ == "__main__":
    unittest.main()
