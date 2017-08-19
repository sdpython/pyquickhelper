"""
@brief      test log(time=100s)
@author     Xavier Dupre

This tesdt must be run last because it screws up with
*test_convert_doc_helper* and *test_full_documentation_module_template*.
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
from src.pyquickhelper.helpgen.conf_path_tools import find_in_PATH, find_latex_path, find_pandoc_path, find_graphviz_dot
from src.pyquickhelper.pycode.ci_helper import is_travis_or_appveyor


class TestPaths(unittest.TestCase):

    def test_paths(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        if is_travis_or_appveyor() not in ("circleci", None):
            return
        exe = find_in_PATH("Microsoft")
        if sys.platform.startswith("win"):
            self.assertTrue(exe is not None)
        else:
            self.assertTrue(exe is None)
        dot = find_graphviz_dot()
        if "dot" not in dot:
            raise Exception('{0}'.format(dot))
        pandoc = find_pandoc_path()
        if sys.platform.startswith("win") and "pandoc" not in pandoc.lower():
            raise Exception('{0}'.format(pandoc))
        latex = find_latex_path()
        if sys.platform.startswith("win") and "latex" not in latex and "miktex" not in latex:
            raise Exception('{0}'.format(latex))


if __name__ == "__main__":
    unittest.main()
