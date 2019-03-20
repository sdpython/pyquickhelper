"""
@brief      test log(time=42s)
"""

import sys
import os
import unittest
import warnings

if "temp_" in os.path.abspath(__file__):
    raise ImportError(
        "this file should not be imported in that location: " +
        os.path.abspath(__file__))

from pyquickhelper.loghelper import fLOG
from pyquickhelper.loghelper.repositories.pygit_helper import get_repo_log, get_file_details, repo_ls
from pyquickhelper.pycode import is_travis_or_appveyor


class TestGitLog(unittest.TestCase):

    def test_log(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        fold = os.path.abspath(os.path.split(__file__)[0])
        root = os.path.join(fold, "..", "..")
        res = get_repo_log(root)
        self.assertTrue(len(res) > 0)
        self.assertTrue(isinstance(res, list))
        self.assertEqual(len(res[0]), 6)
        if "http" not in res[0][-1]:
            warnings.warn(
                "[test_log_file_details_all] Not really expected: {0}".format(res[0]))

    def test_file_detail_src(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        fold = os.path.abspath(os.path.split(__file__)[0])
        root = os.path.join(fold, "..", "..")
        res = get_file_details("setup.py", root)
        self.assertTrue(len(res) > 0)
        self.assertEqual(len(res[0]), 5)

    def test_file_detail_bin(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        fold = os.path.abspath(os.path.split(__file__)[0])
        root = os.path.join(fold, "..", "..")
        res = get_file_details(
            "_unittests/ut_loghelper/data/sample_zip.zip", root)
        self.assertTrue(len(res) > 0)
        self.assertEqual(len(res[0]), 5)

    def test_file_ls(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        fold = os.path.abspath(os.path.split(__file__)[0])
        root = os.path.join(fold, "..", "..")
        res = repo_ls(root)
        self.assertTrue(len(res) > 0)

    def test_log_file_details1(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        fold = os.path.abspath(os.path.split(__file__)[0])
        root = os.path.join(fold, "..", "..")
        res = get_repo_log(root, file_detail=True, subset={'setup.py'})
        self.assertTrue(len(res) > 0)
        self.assertTrue(isinstance(res, list))
        self.assertEqual(len(res[0]), 10)

    def test_log_file_details_all(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        if is_travis_or_appveyor() == "travis":
            # Does not work on travis, probably an issue with git version. Did not check.
            return

        fold = os.path.abspath(os.path.split(__file__)[0])
        root = os.path.join(fold, "..", "..")
        res = get_repo_log(root, file_detail=True)
        self.assertTrue(len(res) > 0)
        self.assertTrue(isinstance(res, list))
        self.assertEqual(len(res[0]), 9)
        count = {}
        for row in res:
            name = row[-3]
            ext = os.path.splitext(name)[-1]
            count[ext] = count.get(ext, 0) + 1
        if ".zip" not in count:
            raise Exception("zip missing\n" + str(count))


if __name__ == "__main__":
    unittest.main()
