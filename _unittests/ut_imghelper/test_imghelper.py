"""
@brief      test log(time=7s)

skip this test for regular run
"""

import sys
import os
import unittest

from pyquickhelper.loghelper import fLOG
from pyquickhelper.pycode import get_temp_folder, ExtTestCase
from pyquickhelper.imghelper.img_helper import zoom_img


class TestImgHelper(ExtTestCase):

    def test_img_zoom(self):
        temp = get_temp_folder(__file__, "temp_img_zoom")
        data = os.path.join(temp, "..", "data", "image.png")
        dest = os.path.join(temp, "image2.png")
        obj = zoom_img(data, factor=0.5, out_file=dest)
        self.assertExists(dest)
        self.assertNotEmpty(obj)
        dest = os.path.join(temp, "image3.png")
        obj = zoom_img(data, max_dim=10, out_file=dest)
        self.assertExists(dest)
        self.assertNotEmpty(obj)

    def test_img_zoom_folder(self):
        temp = get_temp_folder(__file__, "temp_img_zoom_folder")
        data = os.path.join(temp, "..", "data", "*.png")
        dest = os.path.join(temp, "{}")
        obj = zoom_img(data, factor=0.5, out_file=dest)
        dest = os.path.join(temp, "image.png")
        self.assertExists(dest)
        self.assertNotEmpty(obj)


if __name__ == "__main__":
    unittest.main()
