"""
@brief      test log(time=10s)

notebook test
"""

import sys
import os
import unittest
import re
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

from src.pyquickhelper import fLOG, get_temp_folder
from src.pyquickhelper.ipythonhelper import install_notebook_extension, get_installed_notebook_extension, get_jupyter_datadir
from src.pyquickhelper.pycode import is_travis_or_appveyor


class TestNotebookExtensions(unittest.TestCase):

    def test_notebook_extension(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        d = get_jupyter_datadir()
        fLOG("get_jupyter_datadir", d)

        fLOG("extension")
        try:
            ext = get_installed_notebook_extension()
        except FileNotFoundError:
            if is_travis_or_appveyor() == "travis":
                # does not work on travis due to permission error
                warnings.warn(
                    "travis, unable to test TestNotebookExtensions.test_notebook_extension")
                return
            ext = []

        if len(ext) == 0:
            fLOG("installation")
            out = install_notebook_extension()
            fLOG(out)

        fLOG("extension")
        ext = get_installed_notebook_extension()
        assert len(ext) > 0
        for e in ext:
            fLOG(e)
        if "IPython-notebook-extensions-master/usability/search-replace/main" not in ext and \
                'IPython-notebook-extensions-master/nbextensions/usability/search-replace/main' not in ext:
            raise Exception(ext)


if __name__ == "__main__":
    unittest.main()
