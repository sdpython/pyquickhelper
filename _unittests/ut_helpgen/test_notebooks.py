"""
@brief      test log(time=18s)
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

from src.pyquickhelper.loghelper.flog import fLOG, run_cmd
from src.pyquickhelper.helpgen.sphinx_main import process_notebooks, add_notebook_page

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

        temp = os.path.join(path, "temp_nb")
        if not os.path.exists(temp):
            os.mkdir(temp)
        for file in os.listdir(temp):
            os.remove(os.path.join(temp, file))

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

        # to be removed later
        if not sys.platform.startswith("win"):
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
            assert os.path.exists(_)

        fou = [os.path.split(_)[-1] for _ in res]
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
        add_notebook_page(res, file)
        assert os.path.exists(file)

        with open(os.path.join(temp, "example_pyquickhelper.rst"), "r", encoding="utf8") as f:
            text = f.read()
        assert "from pyquickhelper import fLOG\n    fLOG(OutputPrint=False)  # by default" in text
        assert ":linenos:" in text

    def test_short_cmd(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        return
        if sys.platform.startswith("win"):
            return
        home = os.environ["HOME"]
        f = "{0}/github/pyquickhelper/_doc/notebooks/example_pyquickhelper.ipynb".format(
            home)
        fo = "{0}/github/pyquickhelper/_unittests/ut_helpgen/temp_nb/example_pyquickhelper.html".format(
            home)
        if os.path.exists(fo):
            os.remove(fo)
        assert not os.path.exists(fo)
        if os.path.exists(f):
            cmd = '{0}/anaconda3/bin/ipython nbconvert --to html {0}/github/pyquickhelper/_doc/notebooks/example_pyquickhelper.ipynb --template full --output={0}/github/pyquickhelper/_unittests/ut_helpgen/temp_nb/example_pyquickhelper'
            cmd = cmd.format(home)
            out, err = run_cmd(cmd, shell=False, wait=True, communicate=False)
            # fLOG(out)
            # fLOG("******************",err)
            assert "[NbConvertApp] Writing" in err
            if not os.path.exists(fo):
                fLOG(fo)
                fLOG(os.path.abspath(os.path.dirname(fo)))
                fLOG(os.listdir(os.path.dirname(fo)))
                assert False
        else:
            fLOG("unfound ", f)


if __name__ == "__main__":
    unittest.main()
