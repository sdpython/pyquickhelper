"""
@brief      test log(time=2s)
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
from src.pyquickhelper.helpgen.stat_helper import enumerate_notebooks_link


class TestHelpGenStatHelper(unittest.TestCase):

    def test_src_import(self):
        """for pylint"""
        self.assertTrue(src is not None)

    def test_enumerate_notebooks_link(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        this = os.path.abspath(os.path.dirname(__file__))
        nb_folder = os.path.join(this, "..", "..", "_doc", "notebooks")
        self.assertTrue(os.path.exists(nb_folder))
        nb_doc = os.path.join(this, "..", "..", "_doc", "sphinxdoc", "source")
        self.assertTrue(os.path.exists(nb_doc))
        nb = 0
        counts = {'title': 0}
        nbfound = set()
        for r in enumerate_notebooks_link(nb_folder, nb_doc):
            rl = list(r)
            rl[0] = None if r[0] is None else os.path.split(r[0])[-1]
            rl[1] = os.path.split(r[1])[-1]
            nb += 1
            m = rl[2]
            counts[m] = counts.get(m, 0) + 1
            self.assertTrue(r[-2] is None or isinstance(r[-2], str))
            self.assertTrue(r[-1] is None or isinstance(r[-1], str))
            if r[-1] is not None:
                counts["title"] += 1
            nbfound.add(rl[1])
        self.assertTrue(counts.get("ref", 0) > 0)
        self.assertIn(counts.get(None, 0), (0, 10))
        self.assertTrue(counts["title"] > 0)
        self.assertTrue(len(nbfound) > 8)
        # self.assertTrue(counts.get("refn", 0) > 0)
        self.assertIn(counts.get("toctree", 0), (0, 14))


if __name__ == "__main__":
    unittest.main()
