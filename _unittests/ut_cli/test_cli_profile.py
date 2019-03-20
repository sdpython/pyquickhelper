"""
@brief      test tree node (time=7s)
"""


import os
import unittest
from io import StringIO

from pyquickhelper.loghelper import fLOG, BufferedPrint
from pyquickhelper.pycode import ExtTestCase
from pyquickhelper.__main__ import main


def to_profile(args):
    st = BufferedPrint()
    main(args=args, fLOG=st.fprint)
    return str(st)


class TestCliProfile(ExtTestCase):

    def test_profile(self):
        "checks that bokeh is not loaded"
        prof = self.profile(lambda: to_profile(["clean_files", "--help"]))[1]
        self.assertNotIn("bokeh", prof.lower())


if __name__ == "__main__":
    unittest.main()
