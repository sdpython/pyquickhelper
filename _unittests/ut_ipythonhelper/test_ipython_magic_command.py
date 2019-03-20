"""
@brief      test log(time=2s)
"""

import sys
import os
import unittest

from pyquickhelper.loghelper import fLOG
from pyquickhelper.ipythonhelper.magic_class_example import MagicClassExample


class TestMagicCommands (unittest.TestCase):

    def test_magic_commands(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        mg = MagicClassExample()
        mg.add_context({"MagicClassExample": MagicClassExample})
        cmd = "MagicClassExample -f text --no-print"
        fLOG("**", cmd)
        res = mg.htmlhelp(cmd)
        fLOG(res)
        assert "@NB(example of a magic command)"


if __name__ == "__main__":
    unittest.main()
