"""
@brief      test log(time=8s)
@author     Xavier Dupre
"""
import sys
import os
import unittest
from IPython.core.display import Image
from pyquickhelper.pycode import ExtTestCase
from pyquickhelper.helpgen.utils_sphinx_config import NbImage


class TestHelperHelpGen(ExtTestCase):

    def test_NbImage(self):
        r = NbImage("completion.png")
        assert isinstance(r, Image)

    def test_NbImage_url(self):
        r = NbImage(
            'https://github.com/sdpython/pyquickhelper/raw/master/'
            '_doc/sphinxdoc/source/_static/project_ico.png')
        self.assertIsInstance(r, Image)

    def test_NbImage_multi(self):
        r = NbImage("completion.png", "completion.png")
        self.assertIsInstance(r, Image)

    def test_NbImage_url_multi(self):
        r = NbImage(
            'https://github.com/sdpython/pyquickhelper/raw/master/'
            '_doc/sphinxdoc/source/_static/project_ico.png',
            'https://github.com/sdpython/pyquickhelper/raw/master/'
            '_doc/sphinxdoc/source/_static/project_ico.png')
        self.assertIsInstance(r, Image)


if __name__ == "__main__":
    unittest.main()
