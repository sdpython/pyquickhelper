"""
@brief      test log(time=8s)
@author     Xavier Dupre
"""
import os
import unittest
from pyquickhelper.pycode import (
    get_temp_folder, is_travis_or_appveyor, ignore_warnings)
from pyquickhelper.helpgen import rst2html


class TestRst2Html(unittest.TestCase):

    @ignore_warnings(PendingDeprecationWarning)
    def test_rst2html_png(self):
        if is_travis_or_appveyor() in ('travis', 'appveyor'):
            # It requires latex.
            return

        temp = get_temp_folder(__file__, "temp_rst2html_png")
        rst = os.path.join(os.path.abspath(
            os.path.dirname(__file__)), "data", "hermionne.rst")
        with open(rst, "r", encoding="utf-8") as f:
            content = f.read()

        text = rst2html(content)

        ji = os.path.join(temp, "out.html")
        with open(ji, "w", encoding="utf-8") as f:
            f.write(text)
        text2 = rst2html(content, layout="sphinx")
        ji = os.path.join(temp, "out_sphinx.html")
        with open(ji, "w", encoding="utf-8") as f:
            f.write(text)
        self.assertTrue(len(text2) > len(text))

    @ignore_warnings(PendingDeprecationWarning)
    def test_rst2html_svg(self):
        if is_travis_or_appveyor() in ('travis', 'appveyor'):
            # It requires latex.
            return
        temp = get_temp_folder(__file__, "temp_rst2html_svg")
        rst = os.path.join(os.path.abspath(
            os.path.dirname(__file__)), "data", "hermionne.rst")
        with open(rst, "r", encoding="utf-8") as f:
            content = f.read()
        text = rst2html(content, imgmath_image_format='svg')

        ji = os.path.join(temp, "out.html")
        with open(ji, "w", encoding="utf-8") as f:
            f.write(text)
        text2 = rst2html(content, layout="sphinx")
        ji = os.path.join(temp, "out_sphinx.html")
        with open(ji, "w", encoding="utf-8") as f:
            f.write(text)
        self.assertTrue(len(text2) > len(text))

    @ignore_warnings(PendingDeprecationWarning)
    def test_rst2html_plot_rst(self):
        temp = get_temp_folder(__file__, "temp_rst2html_plot_rst")
        rst = os.path.join(os.path.abspath(
            os.path.dirname(__file__)), "data", "rstplot.rst")
        with open(rst, "r", encoding="utf-8") as f:
            content = f.read()

        try:
            text = rst2html(content, document_name="out_string_plot",
                            override_image_directive=True)
        except (OSError, ValueError) as e:
            # Invalid argument: '[...]<string>-1.py'
            self.assertIn("<string>-1.py", str(e))
            return

        ji = os.path.join(temp, "out.html")
        with open(ji, "w", encoding="utf-8") as f:
            f.write(text)

    @ignore_warnings(PendingDeprecationWarning)
    def test_rst2html_plot_html(self):
        temp = get_temp_folder(__file__, "temp_rst2html_plot_html")
        rst = os.path.join(os.path.abspath(
            os.path.dirname(__file__)), "data", "rstplot.rst")
        with open(rst, "r", encoding="utf-8") as f:
            content = f.read()

        try:
            text2 = rst2html(
                content, document_name="out_string_plot", layout="sphinx")
        except OSError as e:
            # Invalid argument: '[...]<string>-1.py'
            self.assertIn("<string>-1.py", str(e))
            return
        ji = os.path.join(temp, "out_sphinx.html")
        with open(ji, "w", encoding="utf-8") as f:
            f.write(text2)


if __name__ == "__main__":
    # TestRst2Html().test_rst2html_plot_rst()
    unittest.main()
