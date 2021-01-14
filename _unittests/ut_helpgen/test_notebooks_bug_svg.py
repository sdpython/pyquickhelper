"""
@brief      test log(time=35s)
@author     Xavier Dupre
"""

import sys
import os
import unittest
from nbconvert.preprocessors.svg2pdf import SVG2PDFPreprocessor
from pyquickhelper.loghelper import fLOG, run_cmd
from pyquickhelper.helpgen.sphinx_main import (
    process_notebooks, setup_environment_for_help)
from pyquickhelper.helpgen.post_process import post_process_latex
from pyquickhelper.pycode import is_travis_or_appveyor, ExtTestCase


class TestNoteBooksBugSvg(ExtTestCase):

    def test_notebook_svg(self):
        """
        If the test fails, look into issue
        `216 <https://github.com/sdpython/pyquickhelper/issues/216>`_.
        Avoid nbconvert==5.4.0,==5.4.1.
        """
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        path = os.path.abspath(os.path.split(__file__)[0])
        fold = os.path.normpath(os.path.join(path, "notebooks_svg"))
        nbs = [os.path.join(fold, _)
               for _ in os.listdir(fold) if ".ipynb" in _]
        formats = ["latex", "pdf"]

        temp = os.path.join(path, "temp_nb_bug_svg")
        if not os.path.exists(temp):
            os.mkdir(temp)
        for file in os.listdir(temp):
            os.remove(os.path.join(temp, file))

        if is_travis_or_appveyor() in ('travis', 'appveyor', 'azurepipe', 'circleci'):
            return

        setup_environment_for_help()
        obj = SVG2PDFPreprocessor()
        self.assertIn('inkscape', obj.inkscape)
        cmd = '%s --version' % obj.inkscape
        out, err = run_cmd(cmd, wait=True, shell=False)
        self.assertIn('inkscape', out.lower())
        vers = obj.inkscape_version
        self.assertIn('inkscape', out.lower())

        res = process_notebooks(nbs, temp, temp, formats=formats)
        for _ in res:
            fLOG(_)
            self.assertExists(_[0])

        with open(os.path.join(temp, "seance4_projection_population_correction.tex"), "r", encoding="utf8") as f:
            content = f.read()
        exp = "seance4_projection_population_correction_50_0.pdf"
        if exp not in content:
            raise Exception(content)

    def test_replace_includgraphics(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        text = """\\usepackage{multirow}
                \\includegraphics{seance4_projection_population_correction_50_0.svg}
                \\begin{enumerate}
                """
        new_text = post_process_latex(text, True, fLOG=fLOG)
        if "%\\includegraphics" not in new_text:
            raise Exception(new_text)


if __name__ == "__main__":
    unittest.main()
