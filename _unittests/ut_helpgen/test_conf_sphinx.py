"""
@brief      test log(time=8s)
@author     Xavier Dupre
"""

import sys
import os
import unittest
import shutil


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
from src.pyquickhelper.helpgen.default_conf import set_sphinx_variables


class TestConfSphinx(unittest.TestCase):

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
        assert os.path.exists(ff)
        import solar_theme
        d = {}
        set_sphinx_variables(
            ff,
            "thisname",
            "XD",
            2014,
            "solar_theme",
            solar_theme.theme_path,
            d)
        for k, v in d.items():
            fLOG(k, "\t=", v)


if __name__ == "__main__":
    unittest.main()
