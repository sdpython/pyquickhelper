"""
@brief      test tree node (time=5s)
"""


import sys
import os
import unittest
import re

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
from src.pyquickhelper.filehelper.file_tree_node import FileTreeNode


class TestFileCol (unittest.TestCase):

    def test_synchro(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        try:
            import pysvn as skip_
        except ImportError:
            fLOG("pysvn is not available")
            return

        path = os.path.split(__file__)[0]
        p1 = os.path.join(path, "data")
        p2 = "c:\\temp\\pyapptemp"
        if not os.path.exists(p2):
            os.mkdir(p2)
        fLOG("form ", p1)
        fLOG("to   ", p2)
        exp = re.compile("[.]svn")

        def filter(root, path, f, d):
            root = root.lower()
            path = path.lower()
            f = f.lower()
            be = os.path.join(path, f)
            if "build" in be:
                return False
            if exp.search(be):
                return False
            return True

        f1 = p1
        f2 = p2

        node1 = FileTreeNode(f1, filter=filter, repository=True)
        node2 = FileTreeNode(f2, filter=filter, repository=False)
        fLOG("number of found files (p1)", len(node1), node1.max_date())
        fLOG("number of found files (p2)", len(node2), node2.max_date())

        res = node1.difference(node2, hash_size=1024 ** 2)
        for r in res:
            if r[0] == ">+":
                r[2].copyTo(p2)

        node1 = FileTreeNode(f1, filter=filter, repository=True)
        node2 = FileTreeNode(f2, filter=filter, repository=False)
        fLOG("number of found files (p1)", len(node1), node1.max_date())
        fLOG("number of found files (p2)", len(node2), node2.max_date())
        res = node1.difference(node2, hash_size=1024 ** 2)
        for r in res:
            if r[0] == "==":
                r[3].remove()


if __name__ == "__main__":
    unittest.main()
