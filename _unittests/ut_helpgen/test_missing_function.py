"""
@brief      test log(time=8s)
@author     Xavier Dupre
"""

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
from src.pyquickhelper.helpgen.utils_sphinx_config import ie_layout_html, NbImage, fix_ie_layout_html
from src.pyquickhelper.helpgen.post_process import remove_character_under32


class TestMissingFunction(unittest.TestCase):

    def test_ie(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        if not sys.platform.startswith("win"):
            return

        if not ie_layout_html():
            r = fix_ie_layout_html()
            self.assertTrue(r)

        if not ie_layout_html():
            warnings.warn("The output is not optimized for IE.")

    def test_nb_image(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        r = NbImage("completion.png")
        self.assertTrue(r is not None)

    def test_remove_character_under32(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        s = "a\na\r"
        s2 = remove_character_under32(s)
        self.assertEqual(s2, 'a a ')


if __name__ == "__main__":
    unittest.main()
