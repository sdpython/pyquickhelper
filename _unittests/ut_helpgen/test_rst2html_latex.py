"""
@brief      test log(time=8s)
@author     Xavier Dupre
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

from src.pyquickhelper.loghelper.flog import fLOG
from src.pyquickhelper.pycode import get_temp_folder, is_travis_or_appveyor
from src.pyquickhelper.helpgen import rst2html

if sys.version_info[0] == 2:
    from codecs import open


class TestRst2HtmlLatex(unittest.TestCase):

    def test_rst2html_png_bug(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        if is_travis_or_appveyor in ('travis', 'appveyor'):
            # It requires latex.
            return

        if sys.version_info[:2] <= (2, 7):
            # i don't want to fix it for Python 2.7
            return

        temp = get_temp_folder(__file__, "temp_rst2html_png_latex")
        rst = os.path.join(os.path.abspath(
            os.path.dirname(__file__)), "data", "puzzle_girafe.rst")
        with open(rst, "r", encoding="utf-8") as f:
            content = f.read()
        text = rst2html(content, fLOG=fLOG, outdir=temp, warnings_log=True,
                        imgmath_latex_preamble="""
                    \\newcommand{\\acc}[1]{\\left\\{#1\\right\\}}
                    \\newcommand{\\cro}[1]{\\left[#1\\right]}
                    \\newcommand{\\pa}[1]{\\left(#1\\right)}
                    \\newcommand{\\girafedec}[3]{ \\begin{array}{ccccc} #1 &=& #2 &+& #3 \\\\ a' &=& a &-& o  \\end{array}}
                    \\newcommand{\\vecteur}[2]{\\pa{#1,\\dots,#2}}
                    \\newcommand{\\R}[0]{\\mathbb{R}}
                    \\newcommand{\\N}[0]{\\mathbb{N}}
                    """)
        # fLOG(text)
        ji = os.path.join(temp, "out.html")
        with open(ji, "w", encoding="utf-8") as f:
            f.write(text)


if __name__ == "__main__":
    unittest.main()
