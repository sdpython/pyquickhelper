"""
@brief      test log(time=4s)
@author     Xavier Dupre
"""
import sys
import os
import unittest
import warnings
import logging
from io import StringIO
from docutils.parsers.rst import directives

from pyquickhelper.loghelper.flog import fLOG
from pyquickhelper.pycode import get_temp_folder, ExtTestCase
from pyquickhelper.helpgen import rst2html
from pyquickhelper.helpgen.sphinxm_custom_app import CustomSphinxApp
from pyquickhelper.sphinxext.sphinximages.sphinxtrib.images import ImageDirective


class TestImageExtension(ExtTestCase):

    def test_post_parse_sn(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        directives.register_directive("image", ImageDirective)

    def test_thumbnail(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        from docutils import nodes as skip_

        content = """
                    test a directive
                    ================

                    before

                    .. thumbnail:: http://www.xavierdupre.fr/app/pyquickhelper/helpsphinx/_static/project_ico.png
                        :width: 10
                        :height: 20
                        :download: 1

                    after

                    this code shoud appear
                    """.replace("                    ", "")
        if sys.version_info[0] >= 3:
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

        warns = log_capture_string.getvalue()
        if warns:
            raise Exception(warns)

        t1 = "this code shoud not appear"
        if t1 in html:
            raise Exception(html)

        t1 = "this code shoud appear"
        if t1 not in html:
            raise Exception(html)

        t1 = "_images"
        if t1 not in html:
            raise Exception(html)

        t1 = "linkedin"
        if t1 in html:
            raise Exception(html)

        temp = get_temp_folder(__file__, "temp_sphinx_thumbnail")
        with open(os.path.join(temp, "out_image.html"), "w", encoding="utf8") as f:
            f.write(html)

    def test_sphinx_ext_thumbnail_html(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        temp = get_temp_folder(__file__, "temp_sphinx_ext_thumbnail_html")
        src_ = os.path.join(temp, "..", "data", "image")

        app = CustomSphinxApp(src_, temp)
        app.build()

        index = os.path.join(temp, "index.html")
        self.assertExists(index)
        img = os.path.join(temp, '_images', 'im.png')
        self.assertExists(img)


if __name__ == "__main__":
    unittest.main()
