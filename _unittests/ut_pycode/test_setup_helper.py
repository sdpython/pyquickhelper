"""
@brief      test tree node (time=1s)
"""


import sys
import os
import unittest

from pyquickhelper.loghelper import fLOG
from pyquickhelper.pycode import available_commands_list


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
