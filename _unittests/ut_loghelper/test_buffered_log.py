"""
@brief      test log(time=0s)
"""

import sys
import os
import unittest
import time

from pyquickhelper.loghelper import BufferedPrint


class TestBufferedLog(unittest.TestCase):

    def test_buffered_log(self):

        def do_something(fLOG=None):
            if fLOG:
                fLOG("Did something.")
            return 3

        buf = BufferedPrint()
        do_something(fLOG=buf.fprint)
        self.assertEqual(str(buf), "Did something.\n")


if __name__ == "__main__":
    unittest.main()
