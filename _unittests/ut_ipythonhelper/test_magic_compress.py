"""
@brief      test log(time=1s)
"""


import sys
import os
import unittest
import warnings

from pyquickhelper.loghelper import fLOG
from pyquickhelper.pycode import get_temp_folder
from pyquickhelper.ipythonhelper.magic_class_compress import MagicCompress


class TestMagicCompress (unittest.TestCase):

    def test_files_compress(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        this = os.path.abspath(__file__)
        temp = get_temp_folder(__file__, "temp_compress")
        dest = os.path.join(temp, "temp_this.zip")

        mg = MagicCompress()
        cmd = "dest [this]"
        fLOG("**", cmd)
        assert not os.path.exists(dest)
        mg.add_context({"this": this, "dest": dest})
        res = mg.compress(cmd)
        fLOG(res)
        assert os.path.exists(dest)
        assert res == 1


if __name__ == "__main__":
    unittest.main()
