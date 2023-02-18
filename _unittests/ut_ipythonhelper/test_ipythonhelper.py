"""
@brief      test log(time=2s)
"""

import sys
import os
import unittest
from pyquickhelper.pycode import ExtTestCase
from pyquickhelper.ipythonhelper import AutoCompletion, AutoCompletionFile, MagicCommandParser, MagicClassWithHelpers, open_html_form


class TestAutoCompletion(ExtTestCase):

    def test_completion(self):
        root = AutoCompletion()
        cl = root._add("name", "TestAutoCompletion")
        cl._add("method", "test_completion")
        cl._add("method2", "test_completion")
        cl = root._add("name2", "TestAutoCompletion2")
        cl._add("method3", "test_completion")
        s = (str  # unicode#
             (root))
        self.assertIn(" |   |- method2", s)
        ls = len(root)
        self.assertEqual(ls, 6)

    def test_completion_file(self):
        fold = os.path.abspath(os.path.split(__file__)[0])
        fold = os.path.join(fold, "..", "..", "src")
        this = AutoCompletionFile(fold)
        ls = len(this)
        self.assertGreater(ls, 30)

    def test_html_form(self):
        params = {"parA": "valueA", "parB": "valueB"}
        title = 'unit_test_title'
        key_save = 'jjj'
        raw = open_html_form(params, title, key_save, raw=True)
        self.assertGreater(len(raw), 1)

    def test_eval(self):
        params = {"x": 3, "y": 4}
        cl = MagicCommandParser(prog="test_command")
        res = cl.eval("x+y", params)
        self.assertEqual(res, 7)

    def test_parse(self):
        parser = MagicCommandParser(prog="test_command",
                                    description='display the first lines of a text file')
        typstr = str  # unicode#
        parser.add_argument('f', type=typstr, help='filename')
        parser.add_argument(
            '-n', '--n',
            type=typstr, default=10,
            help='number of lines to display')
        parser.add_argument(
            '-e',
            '--encoding',
            default="utf8",
            help='file encoding')
        params = {"x": 3, "y": 4}
        res = parser.parse_cmd('this.py -n x+y', context=params)
        self.assertNotEmpty(res)
        r = parser.format_help()
        self.assertIn("usage: test_command", r)
        self.assertEqual(res.n, 7)

    def test_class_magic(self):
        cl = MagicClassWithHelpers()
        self.assertEmpty(cl.Context)

        def call_MagicCommandParser():
            return MagicCommandParser(prog="parser_unittest")
        pa = cl.get_parser(call_MagicCommandParser, name="parser_unittest")
        typstr = str  # unicode#
        pa.add_argument('f', type=typstr, help='filename')
        pa.add_argument('-n', '--n', type=typstr, default=10,
                        help='number of lines to display')
        pa.add_argument('-e', '--encoding', default="utf8",
                        help='file encoding')
        self.assertNotEmpty(pa)
        cl.add_context({"x": 3, "y": 4})
        self.assertEqual(cl.Context, {"x": 3, "y": 4})
        res = cl.get_args('this.py -n x+y', pa)
        if res.n != 7:
            raise AssertionError(f"res.n == {res.n}\nres={res}")


if __name__ == "__main__":
    unittest.main()
