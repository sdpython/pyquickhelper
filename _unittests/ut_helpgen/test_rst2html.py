"""
@brief      test log(time=8s)
@author     Xavier Dupre
"""

import sys
import os
import unittest

try:
    import src
except ImportError:
    path = os.path.normpath(
        os.path.abspath(
            os.path.join(
                os.path.split(__file__)[0],
                "..",
                "..")))
    if path not in sys.path:
        sys.path.append(path)
    import src

from src.pyquickhelper.loghelper.flog import fLOG
from src.pyquickhelper.pycode import get_temp_folder, is_travis_or_appveyor
from src.pyquickhelper.helpgen import rst2html

if sys.version_info[0] == 2:
    from codecs import open


class TestRst2Html(unittest.TestCase):

    def test_rst2html_png(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        if is_travis_or_appveyor() in ('travis', 'appveyor'):
            # It requires latex.
            return
        if sys.version_info[0] == 2:
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

    def test_rst2html_svg(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        if is_travis_or_appveyor() in ('travis', 'appveyor'):
            # It requires latex.
            return
        if sys.version_info[0] == 2:
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

    def test_rst2html_plot_rst(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        temp = get_temp_folder(__file__, "temp_rst2html_plot_rst")
        rst = os.path.join(os.path.abspath(
            os.path.dirname(__file__)), "data", "rstplot.rst")
        with open(rst, "r", encoding="utf-8") as f:
            content = f.read()

        try:
            text = rst2html(content, document_name="out_string_plot")
        except OSError as e:
            # Invalid argument: '[...]<string>-1.py'
            self.assertIn("<string>-1.py", str(e))
            return

        ji = os.path.join(temp, "out.html")
        with open(ji, "w", encoding="utf-8") as f:
            f.write(text)

    def test_rst2html_plot_html(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

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
    unittest.main()
