"""
@brief      test tree node (time=7s)
"""


import sys
import os
import unittest
import warnings

from pyquickhelper.pycode import publish_coverage_on_codecov, ExtTestCase
from pyquickhelper.loghelper.repositories.pygit_helper import GitException


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
