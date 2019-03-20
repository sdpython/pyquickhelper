"""
@brief      test log(time=6s)
"""

import sys
import os
import unittest

from pyquickhelper.ipythonhelper import retrieve_notebooks_in_folder
from pyquickhelper.pycode import ExtTestCase


class TestNotebookAutomation(ExtTestCase):

    def test_notebook_retrieve(self):
        this = os.path.abspath(os.path.dirname(__file__))
        nbfile = os.path.join(this, "..", "..", "_doc", "notebooks")
        self.assertExists(nbfile)
        res = retrieve_notebooks_in_folder(nbfile)
        self.assertNotEmpty(res)


if __name__ == "__main__":
    unittest.main()
