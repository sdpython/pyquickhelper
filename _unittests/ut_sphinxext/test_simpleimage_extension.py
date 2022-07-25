"""
@brief      test log(time=6s)
@author     Xavier Dupre
"""
import os
import unittest
import warnings
import logging
import shutil
from io import StringIO
from docutils.parsers.rst import directives
from pyquickhelper.pycode import (
    get_temp_folder, ExtTestCase, is_travis_or_appveyor)
from pyquickhelper.helpgen import rst2html
from pyquickhelper.sphinxext import SimpleImageDirective
from pyquickhelper.helpgen.sphinxm_custom_app import CustomSphinxApp
from pyquickhelper.helpgen.sphinx_main_helper import compile_latex_output_final
from pyquickhelper.helpgen.conf_path_tools import find_latex_path


class TestSimpleImageExtension(ExtTestCase):

    def test_post_parse_sn(self):
        directives.register_directive("video", SimpleImageDirective)

    def test_simpleimage(self):
        from docutils import nodes as skip_

        this = os.path.abspath(os.path.dirname(__file__))
        img = os.path.join(this, "data", "image", "im.png")
        self.assertExists(img)

        content = """
                    test a directive
                    ================

                    before

                    .. simpleimage:: {0}
                        :width: 10
                        :height: 20
                        :target: https://website
                        :alt: zoo

                    after

                    this code should appear
                    """.replace("                    ", "").format(img)
        content = content.replace('u"', '"')

        logger2 = logging.getLogger("video")

        log_capture_string = StringIO()
        ch = logging.StreamHandler(log_capture_string)
        ch.setLevel(logging.DEBUG)
        logger2.addHandler(ch)
        with warnings.catch_warnings(record=True):
            html = rst2html(content,  # fLOG=fLOG,
                            writer="custom", keep_warnings=True,
                            directives=None)

        warns = log_capture_string.getvalue().strip("\n\r\t ")
        if len(warns) != 0 and 'Unable to find' not in warns:
            raise Exception(f"warnings '{warns}'")

        t1 = "this code should not appear"
        if t1 in html:
            raise Exception(html)

        t1 = "this code should appear"
        if t1 not in html:
            raise Exception(html)

        t1 = "im.png"
        if t1 not in html:
            raise Exception(html)

        t1 = "linkedin"
        if t1 in html:
            raise Exception(html)

        temp = get_temp_folder(__file__, "temp_simpleimage")
        with open(os.path.join(temp, "out_image.html"), "w", encoding="utf8") as f:
            f.write(html)

        self.assertNotIn("pngpng", html)

        md = rst2html(content, writer="md",
                      keep_warnings=True, directives=None)
        self.assertIn("im.png", md)
        self.assertNotIn("pngpng", md)

        lat = rst2html(content, writer="elatex",
                       keep_warnings=True, directives=None)
        self.assertIn("im.png", lat)
        self.assertNotIn("pngpng", lat)
        self.assertIn("includegraphics", lat)

        rst = rst2html(content, writer="rst",
                       keep_warnings=True, directives=None)
        self.assertIn("im.png", rst)
        self.assertNotIn("pngpng", rst)
        self.assertIn("simpleimage::", rst)

        self.assertRaise(lambda: rst2html(content, writer="text", keep_warnings=True, directives=None),
                         ValueError)


if __name__ == "__main__":
    unittest.main()
