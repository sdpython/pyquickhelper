"""
@brief      test log(time=8s)
@author     Xavier Dupre
"""

import sys
import os
import unittest

import pyquickhelper
from pyquickhelper.loghelper import fLOG
from pyquickhelper.helpgen.default_conf import set_sphinx_variables
from pyquickhelper.pycode import is_travis_or_appveyor


class TestConfSphinx(unittest.TestCase):

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
        assert os.path.exists(ff)
        import sphinx_rtd_theme as skip_
        d = {}
        try:
            set_sphinx_variables(
                ff,
                "pyquickhelper",
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
            raise e

        for k, v in sorted(d.items()):
            fLOG(k, "\t=", v)
            if k == 'version':
                self.assertEqual(v.split('.')[:2],
                                 pyquickhelper.__version__.split('.')[:2])


if __name__ == "__main__":
    unittest.main()
