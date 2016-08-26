#-*- coding: utf-8 -*-
"""
@brief      test tree node (time=5s)
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
from src.pyquickhelper.pycode.open_script_file import open_script, detect_encoding


class TestOpenScript(unittest.TestCase):

    def test_open_script(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        s = "éé"
        self.assertEqual(len(s), 2)
        file = __file__.replace(".pyc", ".py")
        enc = detect_encoding(file)
        if enc != "utf-8":
            raise Exception(enc)
        with open_script(file, "r") as f:
            r = f.read()
        assert len(r) > 0


if __name__ == "__main__":
    unittest.main()
