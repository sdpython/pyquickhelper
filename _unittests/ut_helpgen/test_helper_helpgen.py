"""
@brief      test log(time=8s)
@author     Xavier Dupre
"""

import sys
import os
import unittest

from pyquickhelper.loghelper.flog import fLOG
from pyquickhelper.helpgen.utils_sphinx_config import ie_layout_html, locate_image_documentation, NbImage

from IPython.core.display import Image


class TestHelperHelpGen(unittest.TestCase):

    def test_ie_layout_html(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        ie_layout_html()

    def test_ie_layout_html2(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        try:
            r = locate_image_documentation("completion.png")
            fLOG(r)
        except FileNotFoundError:
            pass

    def test_NbImage(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        r = NbImage("completion.png")
        assert isinstance(r, Image)


if __name__ == "__main__":
    unittest.main()
