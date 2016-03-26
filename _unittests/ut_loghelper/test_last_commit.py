"""
@brief      test log(time=10s)
"""

import sys
import os
import unittest
import warnings

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


class TestLastCommit (unittest.TestCase):

    def test_last_commit(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        if sys.version_info[0] == 2:
            warnings.warn("disable on Python 2.7")
            return

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
        for c in last:
            if not ("0" <= c <= "9" or "a" <= c <= "z"):
                raise Exception("last commit is not a hash:" + last + "-" + c)


if __name__ == "__main__":
    unittest.main()
