"""
@brief      test tree node (time=5s)
"""


import sys
import os
import unittest

from pyquickhelper.loghelper import fLOG
from pyquickhelper.pycode import get_call_stack


class TestTraceExecution(unittest.TestCase):

    def test_call_stack(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        res = get_call_stack()
        fLOG(res)
        assert len(res.split("\n")) > 2


if __name__ == "__main__":
    unittest.main()
