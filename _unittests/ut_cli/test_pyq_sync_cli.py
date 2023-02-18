"""
@brief      test tree node (time=7s)
"""


import sys
import os
import unittest

from pyquickhelper.loghelper import fLOG
from pyquickhelper.cli.pyq_sync_cli import pyq_sync
from pyquickhelper.cli.cli_helper import clean_documentation_for_cli


class TestPyqSyncCli(unittest.TestCase):

    def test_pyq_sync_cli(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        rows = []

        def flog(*args):
            rows.append(args)

        pyq_sync(args=['-h'], fLOG=flog)

        r = rows[0][0]
        if not r.startswith("usage: synchronize_folder"):
            raise RuntimeError(r)

    def test_clean_documentation_for_cli(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        text = """
        doc :epkg:`up:h.k` doc
        """
        cleaned = clean_documentation_for_cli(text, 'epkg')
        self.assertIn('doc `up.h.k` doc', cleaned)
        cleaned = clean_documentation_for_cli(
            text, lambda t: t.replace('`', 'j'))
        self.assertIn('doc :epkg:jup:h.kj doc', cleaned)


if __name__ == "__main__":
    unittest.main()
