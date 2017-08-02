"""
@brief      test tree node (time=6s)
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
from src.pyquickhelper.cli import create_cli_parser, call_cli_function


class TestParserFromFunction(unittest.TestCase):

    def test_parser_from_function(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        if sys.version_info[0] == 2:
            # rst2html not tested
            return

        def fpars(anint: int, bstring="r", creal: float=None):
            """
            Builds a unique string with the received information.

            :param anint: one integer
            :param bstring: one string
            :param creal: one real
            :return: concatenation
            """
            return "'{0}' - '{1}' - '{2}'".format(anint, bstring, creal)

        self.assertEqual(fpars(0, "e", 0.5), "'0' - 'e' - '0.5'")
        pars = create_cli_parser(fpars)
        self.assertTrue(pars is not None)
        doc = pars.format_help()
        if ":param" in doc:
            # doctree was not cleaned.
            raise Exception(doc)
        if "Builds a unique string with the received information." not in doc:
            raise Exception(doc)
        if "-b BSTRING, --bstring BSTRING" not in doc:
            raise Exception(doc)
        # fLOG(doc)

    def test_parser_from_function_call(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        if sys.version_info[0] == 2:
            # rst2html not tested
            return

        def fpars(anint: int, bstring="r", creal: float=None, fLOG=print):
            """
            Builds a unique string with the received information.

            :param anint: one integer
            :param bstring: one string
            :param creal: one real
            :return: concatenation
            """
            fLOG("## '{0}' - '{1}' - '{2}' ##".format(anint, bstring, creal))

        rows = []

        def flog(*l):
            rows.append(l)

        call_cli_function(
            fpars, args=["-a", "3", "-b", "ttt", "-c", "5.5"], fLOG=flog)
        self.assertTrue(rows, [("## '3' - 'ttt' - '5.5' ##",)])


if __name__ == "__main__":
    unittest.main()