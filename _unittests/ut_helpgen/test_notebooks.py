"""
@brief      test log(time=15s)
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
from src.pyquickhelper.helpgen.sphinx_main import process_notebooks, build_notebooks_gallery
from src.pyquickhelper.pycode import get_temp_folder
from src.pyquickhelper.pycode import is_travis_or_appveyor


if sys.version_info[0] == 2:
    from codecs import open


class TestNotebookConversion(unittest.TestCase):

    def test_notebook(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        fLOG("---------------------------------------------------", 1)
        self.a_te_st_notebook(1)
        # on the second run, the following error happens
        # jinja2.exceptions.TemplateNotFound: article
        fLOG("---------------------------------------------------", 2)
        self.a_te_st_notebook(2)

    def a_te_st_notebook(self, iteration):

        if sys.version_info[0] == 2:
            return

        path = os.path.abspath(os.path.split(__file__)[0])
        fold = os.path.normpath(
            os.path.join(
                path,
                "..",
                "..",
                "_doc",
                "notebooks"))
        nb = os.path.join(fold, "example_pyquickhelper.ipynb")
        assert os.path.exists(nb)

        temp = get_temp_folder(__file__, "temp_nb_%d" % iteration)

        if sys.platform.startswith("win"):
            p1 = r"C:\Program Files\MiKTeX 2.9\miktex\bin\x64"
            p2 = r"%USERPROFILE%\AppData\Local\Pandoc"
        else:
            p1 = "."
            p2 = "."

        formats = ["slides", "ipynb", "html", "python", "rst", "present"]
        exp = ["example_pyquickhelper.html",
               "example_pyquickhelper.ipynb",
               "example_pyquickhelper.py",
               "example_pyquickhelper.rst",
               "example_pyquickhelper.ipynb",
               "example_pyquickhelper.slides.html",
               "example_pyquickhelper.slides2p.html",
               ]

        if sys.platform.startswith("win"):
            formats.append("latex")
            formats.append("pdf")
            exp.append("example_pyquickhelper.tex")
            exp.append("example_pyquickhelper.pdf")

        if is_travis_or_appveyor() in ('travis', 'appveyor'):
            # It requires pandoc.
            return

        res = process_notebooks(
            nb, temp, temp, latex_path=p1, pandoc_path=p2, formats=formats)
        for _ in res:
            fLOG(_)
            assert os.path.exists(_[0])

        fou = [os.path.split(_[0])[-1] for _ in res]
        fou = [_ for _ in fou if "png" not in _]
        fou = list(sorted(set(fou)))
        exp = list(sorted(set(exp)))
        if len(fou) < len(exp):
            raise Exception("length {0} != {1}\n{2}\n---\n{3}".format(len(fou), len(exp),
                                                                      "\n".join(fou), "\n".join(exp)))
        for i, j in zip(exp, fou):
            if i != j:
                raise Exception(
                    "{0} != {1}\nfou=\n{2}\nexp=\n{3}".format(
                        i, j, str(fou), str(exp)))

        file = os.path.join(temp, "all_notebooks.rst")
        build_notebooks_gallery(
            [_[0] for _ in res if _[0].endswith(".ipynb")], file, keep_temp=True)
        self.assertTrue(os.path.exists(file))

        with open(os.path.join(temp, "example_pyquickhelper.rst"), "r", encoding="utf8") as f:
            text = f.read()
        if "from pyquickhelper.loghelper import fLOG\n    fLOG(OutputPrint=False)  # by default" not in text:
            raise Exception(text)
        if ".. raw:: html" not in text:
            raise Exception(text)


if __name__ == "__main__":
    unittest.main()
