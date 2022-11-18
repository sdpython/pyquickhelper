"""
@brief      test log(time=4s)
@author     Xavier Dupre
"""
import os
import logging
import unittest
import warnings
from io import StringIO
from docutils.parsers.rst import directives
from pyquickhelper.pycode import get_temp_folder, ExtTestCase, skipif_appveyor
from pyquickhelper.helpgen import rst2html
from pyquickhelper.helpgen.sphinxm_custom_app import CustomSphinxApp
from pyquickhelper.sphinxext.sphinximages.sphinxtrib.images import ImageDirective


class TestImageExtension(ExtTestCase):

    def setUp(self):
        logger = logging.getLogger('gdot')
        logger.disabled = True

    def test_post_parse_sn(self):
        directives.register_directive("image", ImageDirective)

    @skipif_appveyor("logging issue")
    def test_image(self):
        from docutils import nodes as skip_

        content = """
                    test a directive
                    ================

                    before

                    .. image:: http://www.xavierdupre.fr/app/pyquickhelper/helpsphinx/_static/project_ico.png
                        :width: 10
                        :height: 20
                        :target: https://somewebsite

                    after

                    this code shoud appear
                    """.replace("                    ", "")
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

        t1 = "project_ico.png"
        if t1 not in html:
            raise Exception(html)

        t1 = "linkedin"
        if t1 in html:
            raise Exception(html)

        temp = get_temp_folder(__file__, "temp_sphinx_image")
        with open(os.path.join(temp, "out_image.html"), "w", encoding="utf8") as f:
            f.write(html)

    @skipif_appveyor("logging issue")
    def test_sphinx_ext_image_html(self):
        temp = get_temp_folder(__file__, "temp_sphinx_ext_image_html")
        src_ = os.path.join(temp, "..", "data", "image")

        # Following warning is due to nbconvert.
        # DeprecationWarning: `nbconvert.exporters.exporter_locator` is deprecated
        # in favor of `nbconvert.exporters.base` since nbconvert 5.0.
        app = CustomSphinxApp(src_, temp)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            app.build()

        index = os.path.join(temp, "index.html")
        self.assertExists(index)
        img = os.path.join(temp, '_images', 'im.png')
        self.assertExists(img)

    @skipif_appveyor("logging issue")
    def test_image_url(self):
        from docutils import nodes as skip_

        content = """
                    test a directive
                    ================

                    before

                    .. image:: http://www.xavierdupre.fr/app/pyquickhelper/helpsphinx/_static/project_ico.png
                        :width: 10
                        :height: 20
                        :target: https://somewebsite

                    after

                    this code shoud appear
                    """.replace("                    ", "")
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

        self.assertNotIn("this code shoud not appear", html)
        self.assertIn("this code shoud appear", html)
        self.assertIn("project_ico.png", html)
        self.assertIn('src="http://', html)

        temp = get_temp_folder(__file__, "temp_sphinx_image_url")
        with open(os.path.join(temp, "out_image.html"), "w", encoding="utf8") as f:
            f.write(html)

    @skipif_appveyor("logging issue")
    def test_image_abspath(self):
        from docutils import nodes as skip_

        content = """
                    test a directive
                    ================

                    before

                    .. image:: project_ico.png
                        :width: 10
                        :height: 20

                    after

                    this code shoud appear
                    """.replace("                    ", "")
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

        self.assertNotIn("this code shoud not appear", html)
        self.assertIn("this code shoud appear", html)
        self.assertIn("project_ico.png", html)

        temp = get_temp_folder(__file__, "temp_sphinx_image_abspath")
        with open(os.path.join(temp, "out_image.html"), "w", encoding="utf8") as f:
            f.write(html)


if __name__ == "__main__":
    unittest.main()
