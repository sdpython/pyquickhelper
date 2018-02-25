"""
@brief      test log(time=30s)
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

from src.pyquickhelper.loghelper import fLOG
from src.pyquickhelper.helpgen import process_notebooks
from src.pyquickhelper.helpgen.sphinx_main import setup_environment_for_help
from src.pyquickhelper.helpgen.post_process import post_process_latex
from src.pyquickhelper.pycode import is_travis_or_appveyor, ExtTestCase


if sys.version_info[0] == 2:
    from codecs import open


class TestNoteBooksBugSvg(ExtTestCase):

    def test_notebook_svg(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        if sys.version_info[0] == 2:
            # does not work on Python 2
            return
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

        if is_travis_or_appveyor() in ('travis', 'appveyor'):
            return

        setup_environment_for_help()

        res = process_notebooks(nbs, temp, temp, formats=formats)
        fLOG("*****", len(res))
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
