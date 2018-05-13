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

from src.pyquickhelper.loghelper import fLOG
from src.pyquickhelper.helpgen.default_conf import set_sphinx_variables
from src.pyquickhelper.pycode import is_travis_or_appveyor


if sys.version_info[0] == 2:
    FileNotFoundError = Exception


class TestConfSphinx(unittest.TestCase):

    def test_src_import(self):
        """for pylint"""
        self.assertTrue(src is not None)

    @unittest.skipIf(sys.version_info[:2] < (3, 6), "Not supported in Python < (3, 6)")
    def test_conf_sphinx(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        ff = os.path.abspath(os.path.dirname(__file__))
        ff = os.path.join(
            ff,
            "..",
            "..",
            "_doc",
            "sphinxdoc",
            "source",
            "conf.py")
        if sys.version_info[0] == 2:
            return
        assert os.path.exists(ff)
        import sphinx_rtd_theme as skip_
        d = {}
        try:
            set_sphinx_variables(
                ff,
                "thisname",
                "XD",
                2014,
                "sphinx_rtd_theme",
                None,  # sphinx_rtd_theme.theme_path,
                d,
                use_mathjax=True)
        except FileNotFoundError as e:
            if "dot.exe" in str(e) and is_travis_or_appveyor() == "appveyor":
                # we skip unless we install graphviz --> too long automated
                # build
                return
            else:
                raise e

        for k, v in d.items():
            fLOG(k, "\t=", v)


if __name__ == "__main__":
    unittest.main()
