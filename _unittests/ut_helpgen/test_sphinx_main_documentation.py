"""
@brief      test log(time=287s)
@author     Xavier Dupre
"""
import sys
import os
import unittest
import warnings
import logging
from docutils.parsers.rst import roles
from sphinx.util.logging import getLogger
import pyquickhelper
from pyquickhelper.loghelper.flog import fLOG, download
from pyquickhelper.loghelper import CustomLog, sys_path_append
from pyquickhelper.helpgen.sphinx_main import generate_help_sphinx
from pyquickhelper.pycode import get_temp_folder


class TestSphinxMainDocumentation(unittest.TestCase):

    def test_sphinx_main_documentation(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        temp = get_temp_folder(__file__, "temp_sphinx_main",
                               clean=__name__ != "__main__")
        root = os.path.join(temp, "..", "data_project", "pp")
        var = "python3_module_template"
        generate_help_sphinx(var, module_name=var, root=root,
                             parallel=1, fLOG=fLOG)


if __name__ == "__main__":
    unittest.main()
