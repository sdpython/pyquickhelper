"""
@brief      test log(time=23s)
@author     Xavier Dupre
"""

import sys
import os
import unittest
import warnings

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

from src.pyquickhelper.loghelper import fLOG, run_cmd
from src.pyquickhelper.helpgen.sphinx_main import process_notebooks, add_notebook_page
from src.pyquickhelper.helpgen.process_notebooks import get_ipython_program
from src.pyquickhelper.pycode import get_temp_folder
from src.pyquickhelper.pycode import is_travis_or_appveyor


if sys.version_info[0] == 2:
    from codecs import open


class TestNotebookConversion (unittest.TestCase):

    def test_notebook(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

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

        temp = get_temp_folder(__file__, "temp_nb")

        if sys.platform.startswith("win"):
            p1 = r"C:\Program Files\MiKTeX 2.9\miktex\bin\x64"
            p2 = r"%USERPROFILE%\AppData\Local\Pandoc"
        else:
            p1 = "."
            p2 = "."

        formats = ["slides", "ipynb", "html", "python", "rst"]
        exp = ["example_pyquickhelper.html",
               "example_pyquickhelper.ipynb",
               "example_pyquickhelper.py",
               "example_pyquickhelper.rst",
               "example_pyquickhelper.ipynb",
               "example_pyquickhelper.slides.html",
               ]

        if sys.platform.startswith("win"):
            formats.append("latex")
            formats.append("pdf")
            exp.append("example_pyquickhelper.tex")
            exp.append("example_pyquickhelper.pdf")

        if is_travis_or_appveyor() is not None:
            # it requires pandoc
            return

        res = process_notebooks(
            nb,
            temp,
            temp,
            latex_path=p1,
            pandoc_path=p2,
            formats=formats)
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
                        i,
                        j,
                        str(fou),
                        str(exp)))

        file = os.path.join(temp, "all_notebooks.rst")
        add_notebook_page([_[0] for _ in res], file)
        assert os.path.exists(file)

        with open(os.path.join(temp, "example_pyquickhelper.rst"), "r", encoding="utf8") as f:
            text = f.read()
        assert "from pyquickhelper.loghelper import fLOG\n    fLOG(OutputPrint=False)  # by default" in text
        assert ":linenos:" in text

    def test_short_cmd(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        temp = get_temp_folder(__file__, "temp_nb_cmd")
        f = os.path.join(
            temp, "..", "notebooks_rst", "having_a_form_in_a_notebook.ipynb")
        fo = os.path.join(temp, "having_a_form_in_a_notebook.html")

        if is_travis_or_appveyor() == "appveyor":
            # disable on appveyor
            return

        ipy = get_ipython_program()
        cmd = '{2} nbconvert --to html {0} --template full --output={1}'
        cmd = cmd.format(f, fo, ipy)
        out, err = run_cmd(cmd, shell=False, wait=True, communicate=False)
        fLOG(out)
        fLOG("******************", err)
        if "[NbConvertApp] Writing" not in err:
            # the output might be disabled
            warnings.warn(
                "[NbConvertApp] Writing is missing.\nOUT\n{0}\nERR\n{1}".format(out, err))
        if not os.path.exists(fo):
            fLOG(fo)
            fLOG(os.path.abspath(os.path.dirname(fo)))
            fLOG(os.listdir(os.path.dirname(fo)))
            assert False
        else:
            fLOG("unfound ", f)


if __name__ == "__main__":
    unittest.main()
