"""
@brief      test log(time=8s)
@author     Xavier Dupre
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

from src.pyquickhelper.loghelper.flog import fLOG
from src.pyquickhelper.helpgen.utils_sphinx_doc_helpers import make_label_index


class TestSmallFunction(unittest.TestCase):

    def test_src_import(self):
        """for pylint"""
        self.assertTrue(src is not None)

    def test_make_label_index(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        title = "abAB_-()56$?"
        res = make_label_index(title, "")
        fLOG("***", title, res)
        assert res == "abAB_-56"

    def test_regular_expressions(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        fold = os.path.abspath(os.path.dirname(__file__))
        ff = os.path.join(fold, "data", "divabsolute.rst")
        with open(ff, "r") as f:
            lines = f.readlines()
        reg = re.compile(
            "([.]{2} raw[:]{2} html[\\n ]+<div[\\n ]+style=.?position:absolute;(.|\\n)*?[.]{2} raw[:]{2} html[\\n ]+</div>)")
        fLOG("nb lines", len(lines))
        merged = "".join(lines).replace("\r", "").replace("\t", "")
        r = reg.findall(merged)
        for _ in r:
            fLOG(_)
        assert len(r) > 0


if __name__ == "__main__":
    unittest.main()
