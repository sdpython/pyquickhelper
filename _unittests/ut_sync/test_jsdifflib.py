"""
@brief      test tree node (time=6s)
"""


from __future__ import print_function
import sys
import os
import unittest
import warnings

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

from src.pyquickhelper.loghelper.flog import fLOG
from src.pyquickhelper.filehelper.visual_sync import create_visual_diff_through_html


class TestJsDiffLib(unittest.TestCase):

    def test_src_import(self):
        """for pylint"""
        self.assertTrue(src is not None)

    def test_jsdifflib(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        try:
            import pymyinstall as skip_
        except ImportError:
            path = os.path.normpath(
                os.path.abspath(
                    os.path.join(
                        os.path.split(__file__)[0],
                        "..",
                        "..",
                        "..",
                        "pymyinstall",
                        "src")))
            if path not in sys.path:
                sys.path.append(path)
            try:
                import pymyinstall as skip_
            except ImportError:
                # we skip
                warnings.warn("unable to test TestJsDiffLib.test_jsdifflib")
                return

        tt = os.path.split(
            src.pyquickhelper.filehelper.visual_sync.__file__)[0]
        ma = tt
        p = create_visual_diff_through_html("a", "b")
        assert len(p) > 0
        assert os.path.exists(os.path.join(ma, "difflib.js"))


if __name__ == "__main__":
    unittest.main()
