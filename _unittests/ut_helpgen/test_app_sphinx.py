"""
@brief      test log(time=100s)
@author     Xavier Dupre

This tesdt must be run last because it screws up with 
*test_convert_doc_helper* and *test_full_documentation_module_template*.
"""

import sys
import os
import unittest
import sphinx
from docutils.parsers.rst import directives

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
from src.pyquickhelper import get_temp_folder
from src.pyquickhelper.helpgen.utils_sphinx_doc import private_migrating_doxygen_doc
from src.pyquickhelper.helpgen import CustomSphinxApp

if sys.version_info[0] == 2:
    from codecs import open


class TestAppSphinx(unittest.TestCase):

    def test_app_sphinx(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        temp = get_temp_folder(__file__, "temp_app_sphinx")
        src = os.path.join(temp, "..", "data", "doc")

        app = CustomSphinxApp(src, temp)
        app.build()
        # app.cleanup()

        index = os.path.join(temp, "index.html")
        assert os.path.exists(index)


if __name__ == "__main__":
    unittest.main()
