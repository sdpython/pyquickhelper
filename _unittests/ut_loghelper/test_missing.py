"""
@brief      test tree node (time=5s)
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

from src.pyquickhelper.loghelper.flog import fLOG
from src.pyquickhelper.loghelper.pqh_exception import PQHException


class TestMissing(unittest.TestCase):

    def test_exception(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        try:
            raise PQHException("error", True)
        except PQHException:
            pass


if __name__ == "__main__":
    unittest.main()
