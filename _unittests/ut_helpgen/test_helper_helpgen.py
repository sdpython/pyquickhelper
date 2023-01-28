"""
@brief      test log(time=8s)
@author     Xavier Dupre
"""
import sys
import os
import unittest
from urllib.error import HTTPError
from IPython.core.display import Image
from pyquickhelper.pycode import ExtTestCase
from pyquickhelper.helpgen.utils_sphinx_config import NbImage


class TestHelperHelpGen(ExtTestCase):

    def test_NbImage(self):
        try:
            r = NbImage("completion.png")
        except HTTPError as e:
            if "Not Found" in str(e):
                return
            raise e
        assert isinstance(r, Image)

    def test_NbImage_url(self):
        try:
            r = NbImage(
                'https://github.com/sdpython/pyquickhelper/raw/master/'
                '_doc/sphinxdoc/source/_static/project_ico.png')
        except HTTPError as e:
            if "Not Found" in str(e):
                return
            raise e
        self.assertIsInstance(r, Image)

    def test_NbImage_multi(self):
        try:
            r = NbImage("completion.png", "completion.png")
        except HTTPError as e:
            if "Not Found" in str(e):
                return
            raise e
        self.assertIsInstance(r, Image)

    def test_NbImage_url_multi(self):
        try:
            r = NbImage(
                'https://github.com/sdpython/pyquickhelper/raw/master/'
                '_doc/sphinxdoc/source/_static/project_ico.png',
                'https://github.com/sdpython/pyquickhelper/raw/master/'
                '_doc/sphinxdoc/source/_static/project_ico.png')
        except HTTPError as e:
            if "Not Found" in str(e):
                return
            raise e
        self.assertIsInstance(r, Image)


if __name__ == "__main__":
    unittest.main()
