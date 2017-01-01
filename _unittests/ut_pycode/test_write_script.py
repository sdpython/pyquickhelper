"""
@brief      test tree node (time=5s)
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

from src.pyquickhelper.loghelper import fLOG
from src.pyquickhelper.pycode import get_temp_folder
from src.pyquickhelper import __blog__
from src.pyquickhelper.pycode.setup_helper import write_module_scripts


class TestWriteScript(unittest.TestCase):

    def test_write_script(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        temp = get_temp_folder(__file__, "temp_write_script")

        res = write_module_scripts(temp, "win32", __blog__)
        assert len(res) > 1
        for c in res:
            assert os.path.exists(c)
            with open(c, "r") as f:
                content = f.read()
            if "__" in content:
                for line in content.split("\n"):
                    if sys.version_info[0] == 2:
                        continue
                    if "__" in line and "sys.path.append" not in line and "__file__" not in line:
                        raise Exception(content)


if __name__ == "__main__":
    unittest.main()
