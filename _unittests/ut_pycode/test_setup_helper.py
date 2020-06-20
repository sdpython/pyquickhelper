"""
@brief      test tree node (time=1s)
"""
import sys
import os
import unittest
from pyquickhelper.pycode.setup_helper import (
    available_commands_list, get_available_build_commands,
    get_script_extension)


class TestSetupHelper(unittest.TestCase):

    def test_commands(self):
        assert available_commands_list(["copy27"])
        assert not available_commands_list(["copy27**"])

    def test_get_available_build_commands(self):
        assert get_available_build_commands()
        assert get_script_extension()


if __name__ == "__main__":
    unittest.main()
