"""
@brief      test tree node (time=25s)
"""


import sys
import os
import unittest
import shutil
from pyquickhelper.pycode import coverage_combine, get_temp_folder, ExtTestCase
from pyquickhelper.pycode.coverage_helper import find_coverage_report
from pyquickhelper.pycode.utils_tests import _modifies_coverage_report


class TestCoverageHelper(ExtTestCase):

    def test_combine(self):

        def process(content):
            if sys.platform.startswith('win'):
                return content
            else:
                return content.replace("\\", "/").replace('//', '/')

        temp = get_temp_folder(__file__, "temp_coverage_combine")
        source = os.path.normpath(os.path.abspath(
            os.path.join(temp, "..", "..", "..")))
        self.assertExists(source)
        cov1 = os.path.join(temp, "..", "data", "_coverage_dumps",
                            "tkinterquickhelper", "3d57ce52", "20191216T1347", '.coverage')
        cov2 = os.path.join(temp, "..", "data", "_coverage_dumps",
                            "tkinterquickhelper", "26f6da91", "20191216T1346", '.coverage')
        covs = [cov1, cov2]
        for cov in covs:
            if not os.path.exists(cov):
                raise FileNotFoundError(cov)
            if not os.path.isfile(cov):
                raise Exception("'{0}' is not a file".format(cov))
        # self.assertRaise(lambda: coverage_combine(covs, temp, source=source + "r", process=process,
        #                                          remove_unexpected_root=True),
        #                 RuntimeError)
        coverage_combine(covs, temp, source=source, process=process)
        index = os.path.join(temp, ".coverage")
        self.assertExists(index)

    def test_modifies_coverage_report(self):
        temp = get_temp_folder(__file__, "temp_coverage_modifies")
        sr = os.path.join(temp, "..", "data", ".coverage")
        shutil.copy(sr, temp)
        name = os.path.join(temp, ".coverage")
        b = "C:\\xavierdupre\\__home_" + "\\GitHub\\tkinterquickhelper"
        bproj = "tkinterquickhelper"
        _modifies_coverage_report(name, [b], bproj)
        with open(name, 'rb') as f:
            content = f.read()
        self.assertIn(b'/', content)


if __name__ == "__main__":
    unittest.main()
