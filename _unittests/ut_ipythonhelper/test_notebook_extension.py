"""
@brief      test log(time=10s)

notebook test
"""

import sys
import os
import unittest
import warnings

from pyquickhelper.loghelper import fLOG
from pyquickhelper.ipythonhelper import install_notebook_extension, get_installed_notebook_extension, get_jupyter_datadir
from pyquickhelper.pycode import is_travis_or_appveyor


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
            if is_travis_or_appveyor() in ("travis", "circleci"):
                # It does not work on travis due to permission error.
                return
            ext = []

        if len(ext) == 0:
            fLOG("installation")
            try:
                out = install_notebook_extension()
            except PermissionError as e:
                warnings.warn(
                    "Unable to install jupyter extensions due to permissions errors: {0}".format(e))
                return
            fLOG(out)

        fLOG("extension")
        ext = get_installed_notebook_extension()
        self.assertTrue(len(ext) > 0)
        for e in ext:
            fLOG(e)
        if "jupyter_contrib_nbextensions-master/src/jupyter_contrib_nbextensions/nbextensions/autoscroll/main" not in ext:
            raise Exception(ext)


if __name__ == "__main__":
    unittest.main()
