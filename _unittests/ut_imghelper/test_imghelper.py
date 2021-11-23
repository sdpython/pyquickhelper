"""
@brief      test log(time=7s)

skip this test for regular run
"""

import sys
import os
import unittest

from pyquickhelper.loghelper import fLOG
from pyquickhelper.pycode import get_temp_folder, ExtTestCase
from pyquickhelper.imghelper.img_helper import (
    zoom_img, white_to_transparency, concat_images)


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
        obj2 = zoom_img(obj, max_dim=10, out_file=dest)
        self.assertEqual(obj.size, obj2.size)

    def test_img_zoom_folder(self):
        temp = get_temp_folder(__file__, "temp_img_zoom_folder")
        data = os.path.join(temp, "..", "data", "image*.png")
        dest = os.path.join(temp, "{}")
        obj = zoom_img(data, factor=0.5, out_file=dest)
        dest = os.path.join(temp, "image.png")
        self.assertExists(dest)
        self.assertNotEmpty(obj)

    def test_transparency(self):
        temp = get_temp_folder(__file__, "temp_transparency")
        data = os.path.join(temp, "..", "data", "image.png")
        dest = os.path.join(temp, "image2.png")
        obj = white_to_transparency(data, out_file=dest)
        self.assertExists(dest)
        self.assertNotEmpty(obj)

    def test_concat_images(self):
        temp = get_temp_folder(__file__, "temp_concat_images")
        data = os.path.join(temp, "..", "data")
        images = [os.path.join(data, 'img%d.png' % (i + 1))
                  for i in range(0, 6)]
        dest = os.path.join(temp, "image2.png")
        res = concat_images(images, out_file=dest, width=600)
        self.assertExists(dest)
        self.assertEqual(res.size[0], 600)

    def test_concat_images4(self):
        temp = get_temp_folder(__file__, "temp_concat_images4")
        data = os.path.join(temp, "..", "data")
        images = [os.path.join(data, 'img%d.png' % (i + 1))
                  for i in range(0, 4)]
        dest = os.path.join(temp, "image2.png")
        res = concat_images(images, out_file=dest, width=600)
        self.assertExists(dest)
        self.assertEqual(res.size[0], 600)


if __name__ == "__main__":
    unittest.main()
