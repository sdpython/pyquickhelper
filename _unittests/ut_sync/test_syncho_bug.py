# -*- coding: utf-8 -*-
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

from src.pyquickhelper.loghelper.flog import fLOG
from src.pyquickhelper.filehelper.synchelper import synchronize_folder, remove_folder


class TestSyncFolder (unittest.TestCase):

    def test_bug_accent(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        data = os.path.abspath(os.path.dirname(__file__))
        fold = os.path.join(data, "data", "bug")
        assert os.path.exists(fold)

        to = os.path.join(data, "temp_bug")
        if os.path.exists(to):
            remove_folder(to)
        os.mkdir(to)
        assert os.path.exists(to)

        synchronize_folder(fold, to, hash_size=0, repo1=False, repo2=False,
                           size_different=True, no_deletion=False, filter=None,
                           filter_copy=None, avoid_copy=False, operations=None,
                           file_date=None, log1=False)

        if sys.version_info[0] == 2:
            return

        assert os.path.exists(
            os.path.join(
                to,
                "bugged",
                "Présentation.pdf.txt"))


if __name__ == "__main__":
    unittest.main()
