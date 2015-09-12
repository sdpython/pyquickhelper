"""
@brief      test log(time=2s)
"""

import sys
import os
import unittest
import re


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

from src.pyquickhelper import fLOG
from src.pyquickhelper.ipythonhelper import AutoCompletion, AutoCompletionFile, MagicCommandParser, MagicClassWithHelpers, open_html_form


class TestAutoCompletion (unittest.TestCase):

    def test_completion(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        root = AutoCompletion()
        cl = root._add("name", "TestAutoCompletion")
        cl._add("method", "test_completion")
        cl._add("method2", "test_completion")
        cl = root._add("name2", "TestAutoCompletion2")
        cl._add("method3", "test_completion")
        s = (str  # unicode#
             (root))
        fLOG("\n" + s)
        assert " |   |- method2" in s
        l = len(root)
        fLOG("l=", l)
        assert l == 6
        fLOG(root._)

    def test_completion_file(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        fold = os.path.abspath(os.path.split(__file__)[0])
        fold = os.path.join(fold, "..", "..", "src")
        this = AutoCompletionFile(fold)
        l = len(this)
        assert l > 30

    def test_html_form(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        params = {"parA": "valueA", "parB": "valueB"}
        title = 'unit_test_title'
        key_save = 'jjj'
        raw = open_html_form(params, title, key_save, raw=True)
        fLOG(raw)
        assert len(raw) > 0

    def test_eval(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        params = {"x": 3, "y": 4}
        cl = MagicCommandParser(prog="test_command")
        res = cl.eval("x+y", params, fLOG=fLOG)
        fLOG(res)
        assert res == 7

    def test_parse(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        parser = MagicCommandParser(prog="test_command",
                                    description='display the first lines of a text file')
        parser.add_argument('f', type=str  # unicode#
                            , help='filename')
        parser.add_argument(
            '-n',
            '--n',
            type=str  # unicode#
            , default=10,
            help='number of lines to display')
        parser.add_argument(
            '-e',
            '--encoding',
            default="utf8",
            help='file encoding')
        params = {"x": 3, "y": 4}
        res = parser.parse_cmd('this.py -n x+y', context=params, fLOG=fLOG)
        fLOG(res.__dict__)
        r = parser.format_help()
        assert "usage: test_command [-h] [-n N] [-e ENCODING] f" in r
        fLOG("###\n", r, "###\n")
        fLOG(parser.usage)
        self.assertEqual(res.n, 7)

    def test_class_magic(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        cl = MagicClassWithHelpers()
        assert cl.Context is None

        def call_MagicCommandParser():
            return MagicCommandParser(prog="parser_unittest")
        pa = cl.get_parser(call_MagicCommandParser, name="parser_unittest")
        pa.add_argument('f', type=str  # unicode#
                        , help='filename')
        pa.add_argument(
            '-n',
            '--n',
            type=str  # unicode#
            ,
            default=10,
            help='number of lines to display')
        pa.add_argument(
            '-e',
            '--encoding',
            default="utf8",
            help='file encoding')
        assert pa is not None
        cl.add_context({"x": 3, "y": 4})
        assert cl.Context == {"x": 3, "y": 4}
        res = cl.get_args('this.py -n x+y', pa, print_function=fLOG)
        fLOG("**RES", res)
        if res.n != 7:
            raise Exception("res.n == {0}\nres={1}".format(res.n, res))


if __name__ == "__main__":
    unittest.main()
