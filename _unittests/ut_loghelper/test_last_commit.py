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

from src.pyquickhelper.loghelper import fLOG, SourceRepository
from src.pyquickhelper.pycode import is_travis_or_appveyor


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
                        "last commit is not a hash: '{0}' - '{1}'".format(last, c))


if __name__ == "__main__":
    unittest.main()
