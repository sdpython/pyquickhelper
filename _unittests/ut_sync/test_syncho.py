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
from src.pyquickhelper.filehelper.synchelper import synchronize_folder, remove_folder


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
        p1 = os.path.abspath(os.path.join(path, "..", "ut_loghelper", "data"))
        p2 = os.path.abspath(os.path.join(path, "pyapptemp"))
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

        fLOG("p1=", p1)
        fLOG("p2=", p2)

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

    def test_synchro2(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        fold = os.path.abspath(os.path.split(__file__)[0])
        data = os.path.join(fold, "data")
        seco = os.path.join(fold, "data", "temp_seco")
        troi = os.path.join(fold, "temp_troi")
        sec2 = os.path.join(troi, "temp_seco")

        stay = os.path.join(sec2, "notfile.txt")
        nocp = os.path.join(seco, "file.txt")

        def filter_copy(file):
            return "temp_seco" not in file
        fLOG(filter_copy(stay), stay)
        assert not filter_copy(stay)

        if os.path.exists(troi):
            remove_folder(troi)

        if not os.path.exists(seco):
            os.mkdir(seco)
        if not os.path.exists(troi):
            os.mkdir(troi)
        if not os.path.exists(sec2):
            os.mkdir(sec2)

        with open(nocp, "w") as f:
            f.write("should not be here")
        with open(stay, "w") as f:
            f.write("should stay")

        if sys.version_info[0] == 2:
            return

        synchronize_folder(data,
                           troi,
                           hash_size=0,
                           repo1=True,
                           filter_copy=filter_copy)

        assert os.path.exists(os.path.join(troi, "sub", "filetwo.txt"))
        assert os.path.exists(stay)
        assert not os.path.exists(stay.replace("notfile.txt", "file.txt"))

if __name__ == "__main__":
    unittest.main()
