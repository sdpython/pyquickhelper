"""
@brief      test log(time=7s)
"""

import sys
import os
import unittest
from pyquickhelper.loghelper import fLOG
from pyquickhelper.pycode import get_temp_folder, ExtTestCase
from pyquickhelper.imghelper.img_export import images2pdf


class TestImgExport(ExtTestCase):

    def test_exports(self):
        temp = get_temp_folder(__file__, "temp_img2pdf")
        data = os.path.join(temp, "..", "data", "image2.jpg")
        datap = os.path.join(temp, "..", "data", "*.jpg")
        dest = os.path.join(temp, "images.pdf")
        res = images2pdf([data, datap], dest)
        self.assertExists(dest)
        self.assertEqual(len(res), 5)

        dest = os.path.join(temp, "images3.pdf")
        res = images2pdf(",".join([data, datap]), dest)
        self.assertExists(dest)
        self.assertEqual(len(res), 5)


if __name__ == "__main__":
    unittest.main()
