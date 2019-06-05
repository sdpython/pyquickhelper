"""
@brief      test tree node (time=7s)
"""

import sys
import os
import unittest
import warnings
from io import StringIO

from pyquickhelper.loghelper import fLOG, BufferedPrint
from pyquickhelper.pycode import ExtTestCase, skipif_travis, skipif_circleci, skipif_azure
from pyquickhelper.__main__ import main


class TestCliMainTkinterHelper(ExtTestCase):

    @skipif_travis('_tkinter.TclError: invalid command name "frame"')
    @skipif_circleci('_tkinter.TclError: invalid command name "frame"')
    @skipif_azure('_tkinter.TclError: invalid command name "frame"')
    def test_main(self):
        from tkinter import TclError
        st = BufferedPrint()
        try:
            win = main(args=['--GUITEST'], fLOG=st.fprint)
        except TclError as e:
            # probably run from a remote machine
            warnings.warn(str(e))
            return
        res = str(st)
        self.assertNotIn("python -m pyquickhelper <command> --help", res)
        self.assertNotEmpty(win)


if __name__ == "__main__":
    unittest.main()
