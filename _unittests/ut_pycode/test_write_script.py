"""
@brief      test tree node (time=5s)
"""


import sys
import os
import unittest

from pyquickhelper.loghelper import fLOG
from pyquickhelper.pycode import get_temp_folder, skipif_appveyor
from pyquickhelper import __blog__
from pyquickhelper.pycode.setup_helper import write_module_scripts


class TestWriteScript(unittest.TestCase):

    @skipif_appveyor("Does not work on appveyor")
    def test_write_script(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        temp = get_temp_folder(__file__, "temp_write_script")

        res = write_module_scripts(temp, "win32", __blog__)
        self.assertTrue(len(res) > 1)
        for c in res:
            if not os.path.exists(c):
                raise FileNotFoundError(c)
            with open(c, "r") as f:
                content = f.read()
            if "__" in content:
                for line in content.split("\n"):
                    if "__" in line and "sys.path.append" not in line and "__file__" not in line:
                        raise Exception(content)


if __name__ == "__main__":
    unittest.main()
