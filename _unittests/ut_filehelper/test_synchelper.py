"""
@brief      test log(time=4s)
"""

import sys
import os
import unittest

if "temp_" in os.path.abspath(__file__):
    raise ImportError(
        "this file should not be imported in that location: " +
        os.path.abspath(__file__))

from pyquickhelper.loghelper import fLOG
from pyquickhelper.pycode import get_temp_folder, ExtTestCase
from pyquickhelper.filehelper import synchronize_folder
from pyquickhelper.loghelper.pqh_exception import PQHException


class TestSyncHelper(ExtTestCase):

    def test_synchronize(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        temp = get_temp_folder(__file__, "temp_synchronize")
        data = os.path.join(temp, '..', 'data')
        synchronize_folder(data, temp, fLOG=fLOG)
        self.assertExists(os.path.join(temp, "loghelper.zip"))

        dest = os.path.join(temp, "dest")
        self.assertRaise(lambda: synchronize_folder(
            data, dest, fLOG=fLOG), PQHException)
        synchronize_folder(data, dest, fLOG=fLOG, create_dest=True)
        self.assertExists(os.path.join(dest, "loghelper.zip"))


if __name__ == "__main__":
    unittest.main()
