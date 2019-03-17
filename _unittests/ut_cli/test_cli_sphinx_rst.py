"""
@brief      test tree node (time=8s)
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

    def test_sphinx_rst_notoctree(self):
        "sphinx rst toctree"
        st = BufferedPrint()
        temp = get_temp_folder(__file__, "temp_sphinx_rst_notoctree")
        name = os.path.join(temp, "..", "data", "piecewise_notoc.rst")
        out = os.path.join(temp, "out")
        res = main(args=['sphinx_rst', '-i', name, '-o', out],
                   fLOG=st.fprint)
        out += ".html"
        self.assertExists(out)
        with open(out, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("pour finalement illustrer", content)

    def test_sphinx_rst_toctree(self):
        "sphinx rst toctree"
        st = BufferedPrint()
        temp = get_temp_folder(__file__, "temp_sphinx_rst_toctree")
        name = os.path.join(temp, "..", "data", "piecewise.rst")
        out = os.path.join(temp, "out")
        res = main(args=['sphinx_rst', '-i', name, '-o', out],
                   fLOG=st.fprint)
        out += ".html"
        self.assertExists(out)
        with open(out, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("pour finalement illustrer", content)
        self.assertIn("contains reference to nonexisting document", content)


if __name__ == "__main__":
    unittest.main()
