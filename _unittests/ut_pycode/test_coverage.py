"""
@brief      test tree node (time=7s)
"""


import sys
import os
import unittest
import warnings

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

from src.pyquickhelper.pycode import publish_coverage_on_codecov, ExtTestCase
from src.pyquickhelper.loghelper.repositories.pygit_helper import GitException


class TestCoverage(ExtTestCase):

    @unittest.skipIf(sys.version_info[0] == 2, reason="strings are not very well handled")
    def test_write_script(self):
        temp = os.path.abspath(os.path.dirname(__file__))
        cov = os.path.join(temp, "data", "coverage", "coverage_report.xml")

        try:
            cmd = publish_coverage_on_codecov(cov, None)
            self.assertNotEmpty(cmd)
        except GitException as e:
            warnings.warn("Not tested due to '{0}'".format(e))


if __name__ == "__main__":
    unittest.main()
