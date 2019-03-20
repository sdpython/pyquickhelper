"""
@brief      test tree node (time=8s)
"""

import sys
import os
import unittest
from io import StringIO

from pyquickhelper.pycode import ExtTestCase, get_temp_folder, skipif_travis, skipif_appveyor
from pyquickhelper.__main__ import main
from pyquickhelper.loghelper import BufferedPrint


class TestCliSphinxRst(ExtTestCase):

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

    @skipif_travis("latex is not installed")
    @skipif_appveyor("latex is not installed")
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

    @skipif_travis("latex is not installed")
    @skipif_appveyor("latex is not installed")
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
