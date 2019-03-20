"""
@brief      test log(time=0s)
"""

import sys
import os
import unittest


if "temp_" in os.path.abspath(__file__):
    raise ImportError(
        "this file should not be imported in that location: " +
        os.path.abspath(__file__))

from pyquickhelper.pycode import get_temp_folder
from pyquickhelper.loghelper import fLOG, CustomLog


class TestCustomLog (unittest.TestCase):

    def test_custom_log(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        temp = get_temp_folder(self.test_custom_log)
        assert temp.endswith("temp_custom_log")
        name = os.path.abspath(os.path.dirname(__file__))
        name = os.path.join(name, "temp_custom_log")
        self.assertEqual(name, temp)

        custom = CustomLog(temp)
        self.assertEqual(custom.filename, "log_custom_000.txt")
        full = custom.fullpath
        assert full.endswith("log_custom_000.txt")
        memo = os.path.join(temp, "log_custom_000.txt")
        assert os.path.exists(memo)

        custom("something", para=4)
        custom("oneline")
        custom("something else", para2=5)

        with open(memo, "r", encoding="utf-8") as f:
            text = f.read()

        assert "para = 4" in text
        assert "para2 = 5" in text
        assert "something" in text
        assert "something else" in text
        assert "oneline" in text
        lines = text.split("\n")
        self.assertEqual(len(lines), 6)


if __name__ == "__main__":
    unittest.main()
