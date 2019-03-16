"""
@brief      test tree node (time=7s)
"""

import sys
import os
import unittest
from io import StringIO

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

from src.pyquickhelper.pycode import ExtTestCase, get_temp_folder
from src.pyquickhelper.__main__ import main
from src.pyquickhelper.loghelper import BufferedPrint


class TestCliSphinxRst(ExtTestCase):

    def test_src_import(self):
        """for pylint"""
        self.assertTrue(src is not None)

    def test_sphinx_rst(self):
        "sphinx rst"
        st = BufferedPrint()
        temp = get_temp_folder(__file__, "temp_sphinx_rst")
        name = os.path.join(temp, "..", "data", "glossary.rst")
        out = os.path.join(temp, "out")
        res = main(args=['sphinx_rst', '-i', name, '-o', out],
                   fLOG=st.fprint)
        out += ".html"
        self.assertExists(out)


if __name__ == "__main__":
    unittest.main()
