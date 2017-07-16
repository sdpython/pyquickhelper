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
from src.pyquickhelper.cli.pyq_sync_cli import pyq_sync


class TestPyqSyncCli(unittest.TestCase):

    def test_pyq_sync_cli(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        if sys.version_info[0] == 2:
            # the module returns the following error
            # ENCODING ERROR WITH Python 2.7, will not fix it
            return

        rows = []

        def flog(*l):
            rows.append(l)

        pyq_sync(args=['-h'], fLOG=flog)

        r = rows[0][0]
        if not r.startswith("usage: synchronize_folder [-h] [--p1 P1] [--p2 P2] [-ha HASH_SIZE] [-r REPO1]"):
            raise Exception(r)


if __name__ == "__main__":
    unittest.main()
