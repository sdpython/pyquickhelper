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
from src.pyquickhelper.pycode import is_travis_or_appveyor


class TestSphinxDocMain (unittest.TestCase):

    def test_sphinx_changes(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        path = os.path.abspath(os.path.split(__file__)[0])
        file = os.path.normpath(os.path.join(path, "..", ".."))
        self.assertTrue(os.path.exists(file))

        if sys.version_info[0] == 2:
            return

        if is_travis_or_appveyor() == "travis":
            # Does not work on travis, probably an issue with git version. Did not check.
            return

        rst = generate_changes_repo(None, file)
        # fLOG(rst[:5000])
        self.assertTrue(len(rst) > 0)
        self.assertIn(".. list-table::", rst)
        self.assertIn("* - #", rst)
        self.assertIn("* - 2138", rst)
        self.assertIn("- 2017-08-25", rst)
        self.assertIn("- catch zip extension", rst)


if __name__ == "__main__":
    unittest.main()
