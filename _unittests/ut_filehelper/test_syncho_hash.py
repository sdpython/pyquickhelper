"""
@brief      test tree node (time=6s)
"""


import sys
import os
import unittest

from pyquickhelper.loghelper.flog import fLOG
from pyquickhelper.pycode import ExtTestCase, get_temp_folder
from pyquickhelper.filehelper.synchelper import synchronize_folder, remove_folder


class TestSynchoHash(ExtTestCase):

    def test_synchro_hash(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        fold = os.path.abspath(os.path.split(__file__)[0])
        data = os.path.join(fold, "data")
        seco = os.path.join(fold, "data", "temp_seco2")
        troi = get_temp_folder(__file__, "temp_troi2")
        sec2 = get_temp_folder(__file__, "temp_seco2")

        temp = os.path.join(fold, "temp_date")
        if not os.path.exists(temp):
            os.mkdir(temp)

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

        file_date = os.path.join(temp, "file_date.txt")
        if os.path.exists(file_date):
            os.remove(file_date)

        a = synchronize_folder(data, troi, hash_size=0, repo1=True, filter_copy=filter_copy,
                               file_date=file_date, log1=True)

        self.assertExists(file_date)
        self.assertExists(os.path.join(troi, "sub", "filetwo.txt"))
        self.assertExists(stay)
        self.assertNotExists(stay.replace("notfile.txt", "file.txt"))

        b = synchronize_folder(data, troi, hash_size=0, repo1=True,
                               filter_copy=filter_copy, file_date=file_date)

        if len(a) not in [6, 7, 8, 9]:
            raise AssertionError(
                "2 or 3 expected but got {}:\n{}".format(
                    len(a), "\n".join([str(_) for _ in a])))
        self.assertEqual(a[0][0], ">+")
        self.assertEqual(a[0][0], a[1][0])
        self.assertEqual(len(b), 0)

        troi2 = os.path.join(fold, "temp_troi3")
        if not os.path.exists(troi2):
            os.mkdir(troi2)

        file_date = os.path.join(temp, "file_date_rem.txt")
        if os.path.exists(file_date):
            os.remove(file_date)

        c = synchronize_folder(troi, troi2, hash_size=0, repo1=False,
                               filter_copy=filter_copy, file_date=file_date)

        onefile = os.path.join(troi, "onefile.txt")
        os.remove(onefile)
        with open(file_date, "r") as f:
            all_b = f.readlines()

        c = synchronize_folder(troi, troi2, hash_size=0, repo1=False,
                               filter_copy=filter_copy, file_date=file_date)

        with open(file_date, "r") as f:
            all_c = f.readlines()
        fLOG(c)
        assert len(c) > 0
        onefile2 = os.path.join(troi2, "onefile.txt")
        assert not os.path.exists(onefile2)

        assert len(all_b) == len(all_c) + 1

        if __name__ != "__main__":
            remove_folder(troi)
            remove_folder(troi2)


if __name__ == "__main__":
    unittest.main()
