"""
@brief      test tree node (time=7s)
"""


import sys
import os
import unittest
import warnings
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

from src.pyquickhelper.loghelper import fLOG
from src.pyquickhelper.pycode import ExtTestCase, skipif_travis, skipif_circleci
from src.pyquickhelper.__main__ import main


class TempBuffer:
    "simple buffer"

    def __init__(self):
        "constructor"
        self.buffer = StringIO()

    def fprint(self, *args, **kwargs):
        "print function"
        mes = " ".join(str(_) for _ in args)
        self.buffer.write(mes)
        self.buffer.write("\n")

    def __str__(self):
        "usual"
        return self.buffer.getvalue()


class TestCliMainTkinterHelper(ExtTestCase):

    def test_src_import(self):
        """for pylint"""
        self.assertTrue(src is not None)

    @skipif_travis('_tkinter.TclError: invalid command name "frame"')
    @skipif_circleci('_tkinter.TclError: invalid command name "frame"')
    def test_main(self):
        from tkinter import TclError
        st = TempBuffer()
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
