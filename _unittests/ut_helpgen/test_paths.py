"""
@brief      test log(time=100s)
@author     Xavier Dupre

This tesdt must be run last because it screws up with
*test_convert_doc_helper* and *test_full_documentation_module_template*.
"""

import sys
import os
import unittest

from pyquickhelper.loghelper.flog import fLOG
from pyquickhelper.helpgen.conf_path_tools import find_in_PATH, find_latex_path, find_pandoc_path, find_graphviz_dot
from pyquickhelper.pycode.ci_helper import is_travis_or_appveyor


class TestPaths(unittest.TestCase):

    def test_paths(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        if is_travis_or_appveyor() in ('travis', 'appveyor'):
            return
        exe = find_in_PATH("Microsoft")
        if sys.platform.startswith("win"):
            self.assertTrue(exe is not None)
        else:
            self.assertTrue(exe is None)
        dot = find_graphviz_dot()
        if "dot" not in dot:
            raise AssertionError(f'{dot}')
        pandoc = find_pandoc_path()
        if sys.platform.startswith("win") and "pandoc" not in pandoc.lower():
            raise AssertionError(f'{pandoc}')
        latex = find_latex_path()
        if sys.platform.startswith("win") and "latex" not in latex and "miktex" not in latex:
            raise AssertionError(f'{latex}')


if __name__ == "__main__":
    unittest.main()
