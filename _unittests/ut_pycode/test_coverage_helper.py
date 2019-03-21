"""
@brief      test tree node (time=25s)
"""


import sys
import os
import unittest

from pyquickhelper.pycode import coverage_combine, get_temp_folder, ExtTestCase
from pyquickhelper.pycode.coverage_helper import find_coverage_report


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
                            "tkinterquickhelper", "ba594812", "20171226T1558", '.coverage')
        cov2 = os.path.join(temp, "..", "data", "_coverage_dumps",
                            "tkinterquickhelper", "e2b9d854", "20171226T1418", '.coverage')
        covs = [cov1, cov2]
        for cov in covs:
            if not os.path.exists(cov):
                raise FileNotFoundError(cov)
            if not os.path.isfile(cov):
                raise Exception("'{0}' is not a file".format(cov))
        self.assertRaise(lambda: coverage_combine(covs, temp, source=source + "r", process=process,
                                                  remove_unexpected_root=True),
                         RuntimeError)
        coverage_combine(covs, temp, source=source, process=process,
                         remove_unexpected_root=True)
        index = os.path.join(temp, "index.html")
        self.assertExists(index)

    def test_find_coverage_report(self):
        this = os.path.dirname(__file__)
        data = os.path.join(this, "data", "_coverage_dumps",
                            "tkinterquickhelper")
        find = find_coverage_report(data)
        self.assertIsInstance(find, dict)
        self.assertEqual(len(find), 2)
        exp_ = 'data\\_coverage_dumps\\tkinterquickhelper\\ba594812\\20171226T1558\\.coverage'.replace(
            "\\", "/")
        found = list(sorted(find.items()))[0]
        found_ = "data" + found[1][0].replace("\\", "/").split("data")[-1]
        found = (found[0], (found_, found[1][1], found[1][2]))
        exp = ('ba594812', (exp_, 'pyquickhelper_UT_SKIP_36', '17'))
        self.assertEqual(found, exp)

    def test_combine2(self):

        def process(content):
            if sys.platform.startswith('win'):
                return content
            else:
                return content.replace("\\", "/").replace('//', '/')

        temp = get_temp_folder(__file__, "temp_coverage_combine2")
        source = os.path.normpath(os.path.abspath(
            os.path.join(temp, "..", "..", "..")))
        self.assertExists(source)
        cov1 = os.path.join(temp, "..", "data", "pyq.coverage0")
        cov2 = os.path.join(temp, "..", "data", "pyq.coverage1")
        covs = [cov1, cov2]

        coverage_combine(covs, temp, source=source, process=process,
                         remove_unexpected_root=True)
        index = os.path.join(temp, "index.html")
        self.assertExists(index)


if __name__ == "__main__":
    TestCoverageHelper().test_combine()
    unittest.main()
