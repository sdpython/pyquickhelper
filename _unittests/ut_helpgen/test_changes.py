"""
@brief      test log(time=8s)
@author     Xavier Dupre
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
from src.pyquickhelper.helpgen.sphinx_main import generate_changes_repo


class TestChanges (unittest.TestCase):

    def test_changes(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        path = os.path.abspath(os.path.split(__file__)[0])
        fold = os.path.join(path, "..", "..")
        if os.path.exists(fold):
            fLOG("in")
            file = os.path.join(path, "out_table.rst")
            if os.path.exists(file):
                os.remove(file)
            generate_changes_repo(file, fold)
            with open(file, "r", encoding="utf8") as f:
                content = f.read()
            assert ".. plot::" in content
            content = content[
                content.find("List of recent changes:"):].split("\n")
            ls = [len(_) for _ in content]
            ml = max(ls)
            total = [l for l in ls if ml - 100 <= l < ml]
            assert len(ls) > 0 and len(total) == 0
        else:
            fLOG(
                "sorry, fixing a specific case on another project for accent problem")


if __name__ == "__main__":
    unittest.main()
