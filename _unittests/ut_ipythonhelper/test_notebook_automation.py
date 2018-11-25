"""
@brief      test log(time=6s)
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

from src.pyquickhelper.ipythonhelper import retrieve_notebooks_in_folder
from src.pyquickhelper.pycode import ExtTestCase


class TestNotebookAutomation(ExtTestCase):

    def test_notebook_retrieve(self):
        this = os.path.abspath(os.path.dirname(__file__))
        nbfile = os.path.join(this, "..", "..", "_doc", "notebooks")
        self.assertExists(nbfile)
        res = retrieve_notebooks_in_folder(nbfile)
        self.assertNotEmpty(res)


if __name__ == "__main__":
    unittest.main()
