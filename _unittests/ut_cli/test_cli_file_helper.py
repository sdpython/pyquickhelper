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
from src.pyquickhelper.pycode import get_temp_folder
from src.pyquickhelper.__main__ import main


class TestCliFileHelper(unittest.TestCase):

    def test_src_import(self):
        """for pylint"""
        self.assertTrue(src is not None)

    def test_cli_file_helper(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        this = os.path.abspath(os.path.dirname(__file__))
        st = BufferedPrint()
        main(args=["ls", "-f", this, "-p",
                   ".*[.]py", "-r", "f"], fLOG=st.fprint)
        res = str(st)
        self.assertIn(".py", res)

        this = os.path.abspath(os.path.dirname(__file__))
        st = BufferedPrint()
        main(args=["ls", "-f", this, "-p", ".*[.]py", "-r",
                   "f", '-n', 'pycache', '-fu', '1'],
             fLOG=st.fprint)
        res = str(st)
        self.assertIn(".py", res)
        self.assertNotIn("pycache", res)

        this = os.path.abspath(os.path.dirname(__file__))
        st = BufferedPrint()
        main(args=["ls", "-f", this, "-p", ".*[.]py", "-r",
                   "f", '-n', 'pycache', '-fu', '1', '-s', "test_(.*)",
                   '-su', 'unit_\\1'],
             fLOG=st.fprint)
        res = str(st)
        self.assertIn(".py", res)
        self.assertNotIn("pycache", res)
        self.assertNotIn("test_parser", res)
        self.assertIn("unit_parser", res)


if __name__ == "__main__":
    unittest.main()
