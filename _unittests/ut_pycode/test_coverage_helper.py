"""
@brief      test tree node (time=6s)
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
from src.pyquickhelper.pycode import coverage_combine, get_temp_folder, ExtTestCase


class TestCoverageHelper(ExtTestCase):

    def test_combine(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        def process(content):
            if sys.platform.startswith('win'):
                return content
            else:
                return content.replace("\\", "/")

        temp = get_temp_folder(__file__, "temp_coverage_combine")
        source = os.path.normpath(os.path.abspath(
            os.path.join(temp, "..", "..", "..")))
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
        coverage_combine(covs, temp, source=source, process=process)
        index = os.path.join(temp, "index.html")
        self.assertExists(index)


if __name__ == "__main__":
    unittest.main()
