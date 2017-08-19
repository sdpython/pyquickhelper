"""
@brief      test log(time=0s)
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
from src.pyquickhelper.filehelper import explore_folder_iterfile
from src.pyquickhelper.ipythonhelper import upgrade_notebook, remove_execution_number


class TestConvertNotebooks(unittest.TestCase):

    def test_convert_notebooks(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        fold = os.path.abspath(os.path.dirname(__file__))
        fold2 = os.path.normpath(
            os.path.join(fold, "..", "..", "_doc", "notebooks"))
        for nbf in explore_folder_iterfile(fold2, pattern=".*[.]ipynb"):
            fLOG(nbf)
            with open(nbf, "r", encoding="utf-8") as f:
                content = f.read()
            fLOG(list(content[:10]))
            t = upgrade_notebook(nbf)
            if t:
                fLOG("modified", nbf)
            # remove numbers
            remove_execution_number(nbf, nbf)

        fold2 = os.path.normpath(os.path.join(fold, "..", "..", "_unittests"))
        for nbf in explore_folder_iterfile(fold2, pattern=".*[.]ipynb"):
            fLOG(nbf)
            with open(nbf, "r", encoding="utf-8") as f:
                content = f.read()
            fLOG(list(content[:10]))
            t = upgrade_notebook(nbf)
            if t:
                fLOG("modified", nbf)


if __name__ == "__main__":
    unittest.main()
    