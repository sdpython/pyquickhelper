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
from src.pyquickhelper.pycode import available_commands_list


class TestSetupHelper(unittest.TestCase):

    def test_commands(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        assert available_commands_list(["copy27"])
        assert not available_commands_list(["copy27**"])


if __name__ == "__main__":
    unittest.main()
