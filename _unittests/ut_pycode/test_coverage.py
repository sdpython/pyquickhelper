"""
@brief      test tree node (time=5s)
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
from src.pyquickhelper.pycode import publish_coverage_on_codecov
from src.pyquickhelper.loghelper.repositories.pygit_helper import GitException


class TestCoverage(unittest.TestCase):

    def test_write_script(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        if sys.version_info[0] == 2:
            return

        temp = os.path.abspath(os.path.dirname(__file__))
        cov = os.path.join(temp, "data", "coverage", "coverage_report.xml")

        try:
            cmd = publish_coverage_on_codecov(cov, None)
            assert cmd is not None
        except GitException:
            pass


if __name__ == "__main__":
    unittest.main()
