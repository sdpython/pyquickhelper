"""
@brief      test log(time=2s)
"""

import sys
import os
import unittest

from pyquickhelper.pycode import ExtTestCase
from pyquickhelper.ipythonhelper.magic_class_example import MagicClassExample


class TestMagicCommands(ExtTestCase):

    def test_magic_commands(self):
        mg = MagicClassExample()
        mg.add_context({"MagicClassExample": MagicClassExample})
        cmd = "MagicClassExample -f text --no-print"
        res = mg.htmlhelp(cmd)
        self.assertNotIn("@NB(example of a magic command)", res)


if __name__ == "__main__":
    unittest.main()
