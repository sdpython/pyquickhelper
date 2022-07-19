# coding: utf-8
"""
@brief      test log(time=1s)
"""

import sys
import os
import unittest

from pyquickhelper.loghelper.flog import fLOG
import pyquickhelper.filehelper.synchelper as foldermod


class TestFolder (unittest.TestCase):

    def test_synchronize(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        thispath = os.path.abspath(os.path.split(__file__)[0])
        cache = os.path.join(thispath, "temp_synchro")
        if not os.path.exists(cache):
            os.mkdir(cache)

        remone = os.path.join(cache, "test_log.py")
        fLOG("existing file", remone)
        if os.path.exists(remone):
            os.remove(remone)

        try:
            import pysvn as skip_
        except ImportError:
            return

        all = []
        action = foldermod.synchronize_folder(os.path.join(thispath, "..", "ut_loghelper"), cache, hash_size=0, repo1=True,
                                              operations=lambda a, b, c: all.append(a))
        assert len(all) > 0

        action = foldermod.synchronize_folder(
            os.path.join(
                thispath,
                "..",
                "ut_loghelper"),
            cache,
            hash_size=0,
            repo1=True)
        assert os.path.exists(cache)
        assert len(os.listdir(cache)) > 0
        assert os.path.exists(os.path.join(cache, "data"))
        assert len(os.listdir(os.path.join(cache, "data"))) > 0
        assert len(action) > 0

    def test_synchronize_nosvn(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        thispath = os.path.abspath(os.path.split(__file__)[0])
        if len(thispath) == 0:
            thispath = "./../ut_loghelper"
        cache = os.path.join(thispath, "temp_synchro_nosvn")
        if not os.path.exists(cache):
            os.mkdir(cache)

        remone = os.path.join(cache, "test_log.py")
        fLOG("existing file", remone)
        if os.path.exists(remone):
            os.remove(remone)

        action = foldermod.synchronize_folder(os.path.join(thispath, "..", "ut_loghelper"), cache, hash_size=0, repo1=False,
                                              filter=lambda v: "temp" not in v)
        assert os.path.exists(cache)
        assert len(os.listdir(cache)) > 0
        assert os.path.exists(os.path.join(cache, "data"))
        assert len(os.listdir(os.path.join(cache, "data"))) > 0
        assert len(action) > 0

    def test_remove_folder(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        thispath = os.path.abspath(os.path.split(__file__)[0])
        cache = os.path.join(thispath, "temp_remove")
        if not os.path.exists(cache):
            os.mkdir(cache)

        remone = os.path.join(cache, os.path.split(__file__)[-1])
        fLOG("existing file", remone)
        if os.path.exists(remone):
            os.remove(remone)

        try:
            import pysvn as skip__
        except ImportError:
            return

        action = foldermod.synchronize_folder(
            thispath,
            cache,
            hash_size=0,
            repo1=True)
        ac = foldermod.remove_folder(cache, True)
        assert len(ac) > 0
        for a in ac:
            assert not os.path.exists(a[0])
        act = [_[1].name for _ in action]
        ac = [_[0].split("\\temp_remove\\")[-1] for _ in ac]
        for a in act:
            if a not in ac:
                fLOG("a", a)
                fLOG(ac[0], ac)
                raise Exception(f"a not in ac a={a}, ac={str(ac)}")
            assert a in ac


if __name__ == "__main__":
    unittest.main()
