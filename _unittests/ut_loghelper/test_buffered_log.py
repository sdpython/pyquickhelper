"""
@brief      test log(time=0s)
"""

import sys
import os
import unittest
import time


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


from src.pyquickhelper.loghelper import BufferedPrint


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
