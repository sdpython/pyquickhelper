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
from src.pyquickhelper.pycode.coverage_helper import find_coverage_report
from src.pyquickhelper.loghelper.repositories.pygit_helper import clone


class TestLONGCoverageCombine(ExtTestCase):

    def test_combine(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

    def test_find_combine_coverage_report(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        def process(content):
            if sys.platform.startswith('win'):
                return content
            else:
                return content.replace("\\", "/")

        temp = get_temp_folder(
            __file__, "temp_coverage_find_combine", clean=False)
        gg = os.path.join(temp, '.git')
        if not os.path.exists(gg):
            clone(temp, "github.com", "sdpython", "code_beatrix", fLOG=fLOG)
        this = os.path.abspath(os.path.dirname(__file__))
        data = os.path.join(this, "data", "_coverage_dumps", "code_beatrix")
        find = find_coverage_report(data)
        files = [_[0] for _ in find.values()]
        coverage_combine(files, temp, source=temp, process=process)
        index = os.path.join(temp, 'index.html')
        with open(index, 'r') as f:
            content = f.read()
        content = content.replace('\n', '').replace('\r', '').replace(' ', '')
        self.assertNotIn(
            '<h1>Coveragereport:<span class="pc_cov">82%</span></h1>', content)


if __name__ == "__main__":
    unittest.main()
