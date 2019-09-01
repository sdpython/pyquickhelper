"""
@brief      test tree node (time=7s)
"""

import sys
import os
import unittest
import warnings
from io import StringIO

from pyquickhelper.loghelper import fLOG, BufferedPrint
from pyquickhelper.pycode import ExtTestCase, get_temp_folder
from pyquickhelper.__main__ import main


class TestCliImgHelper(ExtTestCase):

    def test_zoom_img_help(self):
        st = BufferedPrint()
        main(args=['zoom_img', '--help'], fLOG=st.fprint)
        res = str(st)
        self.assertIn("zoom_img [-h]", res)

    def test_zoom_img_do(self):
        temp = get_temp_folder(__file__, 'temp_img_zoom')
        dest = os.path.join(temp, '{}')
        data = os.path.join(temp, '..', 'data', '*.png')
        st = BufferedPrint()
        win = main(args=['zoom_img', '-f', '0.5', '--img',
                         data, '-o', dest], fLOG=st.fprint)
        res = str(st)
        self.assertNotIn("zoom_img [-h]", res)
        self.assertIn("Writing '", res)


if __name__ == "__main__":
    unittest.main()
