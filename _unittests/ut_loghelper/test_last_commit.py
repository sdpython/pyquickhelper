"""
@brief      test log(time=10s)
"""

import sys
import os
import unittest


if "temp_" in os.path.abspath(__file__):
    raise ImportError(
        "this file should not be imported in that location: " +
        os.path.abspath(__file__))

from pyquickhelper.loghelper import fLOG, SourceRepository
from pyquickhelper.pycode import is_travis_or_appveyor


class TestLastCommit (unittest.TestCase):

    def test_last_commit(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        path = os.path.abspath(os.path.dirname(__file__))
        fold = os.path.normpath(os.path.join(path, "..", ".."))

        src_ = SourceRepository()
        res = src_.log(fold)
        for r in res:
            fLOG(len(r), r[-2])
            for i, _ in enumerate(r):
                fLOG(i, _)
            break

        last = src_.get_last_commit_hash()
        if is_travis_or_appveyor() == "circleci":
            self.assertTrue(last is not None)
        else:
            for c in last:
                if not ("0" <= c <= "9" or "a" <= c <= "z"):
                    raise Exception(
                        f"last commit is not a hash: '{last}' - '{c}'")


if __name__ == "__main__":
    unittest.main()
