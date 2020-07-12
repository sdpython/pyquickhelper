"""
@brief      test log(time=7s)

skip this test for regular run
"""

import sys
import os
import unittest

from pyquickhelper.loghelper import fLOG
from pyquickhelper.pycode import get_temp_folder, ExtTestCase, skipif_appveyor
from pyquickhelper.imghelper.svg_helper import svg2img, guess_svg_size


class TestSvg2Image(ExtTestCase):

    @unittest.skipIf(sys.version_info[:2] < (3, 6), "Python 3.5- returns false results.")
    @skipif_appveyor("cannot load library 'libcairo.so': error 0x7e")
    def test_svg2img(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        temp = get_temp_folder(__file__, "temp_svg2png")

        svg = """<svg width="200" height="180">
                 <rect x="50" y="20" width="150" height="150" style="fill:blue;stroke:pink;fill-opacity:0.1;" />
                 <ellipse cx="40" cy="50" rx="20" ry="30" style="fill:yellow" />
                 <ellipse cx="20" cy="50" rx="90" ry="20" style="fill:white" />
                 </svg>
                 """
        img = svg2img(svg)
        name = os.path.join(temp, "image.png")
        img.save(name)
        self.assertExists(name)

        svg = """<svg>
                 <rect x="50" y="20" width="150" height="150" style="fill:blue;stroke:pink;fill-opacity:0.1;" />
                 <ellipse cx="40" cy="50" rx="20" ry="30" style="fill:yellow" />
                 <ellipse cx="20" cy="50" rx="90" ry="20" style="fill:white" />
                 </svg>
                 """

        size = guess_svg_size(svg)
        self.assertEqual(size, (180, 40))

        img = svg2img(svg)
        name = os.path.join(temp, "image2.png")
        img.save(name)
        self.assertExists(name)

        img = svg2img(svg, dpi=200)
        name = os.path.join(temp, "image3.png")
        img.save(name)
        self.assertExists(name)

        img = svg2img(svg, scale=2.)
        name = os.path.join(temp, "image4.png")
        img.save(name)
        self.assertExists(name)


if __name__ == "__main__":
    unittest.main()
