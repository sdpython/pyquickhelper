"""
@brief      test tree node (time=7s)
"""


import sys
import os
import unittest
from io import StringIO

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

from src.pyquickhelper.loghelper import fLOG, BufferedPrint
from src.pyquickhelper.pycode import ExtTestCase
from src.pyquickhelper.__main__ import main


def to_profile(args):
    st = BufferedPrint()
    main(args=args, fLOG=st.fprint)
    return str(st)


class TestCliProfile(ExtTestCase):

    def test_src_import(self):
        """for pylint"""
        self.assertTrue(src is not None)

    def test_profile(self):
        "checks that bokeh is not loaded"
        prof = self.profile(lambda: to_profile(["clean_files", "--help"]))[1]
        self.assertNotIn("bokeh", prof.lower())


if __name__ == "__main__":
    unittest.main()
