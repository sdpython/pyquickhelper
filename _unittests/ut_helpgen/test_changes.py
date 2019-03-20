"""
@brief      test log(time=8s)
@author     Xavier Dupre
"""

import sys
import os
import unittest

from pyquickhelper.loghelper.flog import fLOG
from pyquickhelper.helpgen.sphinx_main import generate_changes_repo


class TestChanges (unittest.TestCase):

    def test_changes(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        path = os.path.abspath(os.path.split(__file__)[0])
        fold = os.path.join(path, "..", "..")
        fold = os.path.normpath(fold)
        if os.path.exists(fold):
            fLOG("exists", fold)
            file = os.path.join(path, "out_table.rst")
            if os.path.exists(file):
                os.remove(file)

            def modifiy_commit(nbch, date, author, comment):
                return nbch, date, author, comment

            generate_changes_repo(file, fold)
            with open(file, "r", encoding="utf8") as f:
                content = f.read()
            self.assertIn(".. plot::", content)
            content = content[
                content.find("List of recent changes:"):]
            self.assertTrue(len(content) > 0)
            self.assertIn(":widths: auto", content)
        else:
            fLOG(
                "sorry, fixing a specific case on another project for accent problem")


if __name__ == "__main__":
    unittest.main()
