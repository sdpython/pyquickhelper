"""
@brief      test log(time=8s)
@author     Xavier Dupre
"""

import sys
import os
import unittest

from pyquickhelper.helpgen.sphinx_main import generate_changes_repo
from pyquickhelper.pycode import is_travis_or_appveyor


class TestSphinxDocMain (unittest.TestCase):

    def test_sphinx_changes(self):
        path = os.path.abspath(os.path.split(__file__)[0])
        file = os.path.normpath(os.path.join(path, "..", ".."))
        self.assertTrue(os.path.exists(file))

        rst = generate_changes_repo(None, file)
        # fLOG(rst[:5000])
        self.assertTrue(len(rst) > 0)
        self.assertIn(".. list-table::", rst)
        self.assertIn("* - #", rst)
        if is_travis_or_appveyor() != "travis":
            self.assertIn("* - 2138", rst)
            self.assertIn("- 2017-08-25", rst)
            self.assertIn("- catch zip extension", rst)


if __name__ == "__main__":
    unittest.main()
