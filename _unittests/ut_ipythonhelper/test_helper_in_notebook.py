"""
@brief      test log(time=2s)
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

from src.pyquickhelper.loghelper import fLOG
from src.pyquickhelper.ipythonhelper import store_notebook_path, add_notebook_menu


class TestHelperInNotebook(unittest.TestCase):

    def test_store_notebook_path(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        r = store_notebook_path()
        assert r is not None

    def test_add_notebook_menu(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        r = add_notebook_menu()
        assert r is not None

if __name__ == "__main__":
    unittest.main()
