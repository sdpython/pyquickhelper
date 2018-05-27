"""
@brief      test log(time=4s)
@author     Xavier Dupre
"""

import sys
import os
import unittest
import warnings
from docutils.parsers.rst import directives

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
from src.pyquickhelper.pycode import get_temp_folder
from src.pyquickhelper.helpgen import rst2html, rst2rst_folder
from src.pyquickhelper.sphinxext import TocDelayDirective


class TestTocDelayExtension(unittest.TestCase):

    def test_post_parse(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        directives.register_directive("tocdelay", TocDelayDirective)

    def test_regex(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        s = "2016-06-11 - Make a reference to a blog post <2016/2016-06-11_blogpost_with_label>"
        reg = TocDelayDirective.regex_title
        gr = reg.search(s)
        self.assertTrue(gr is not None)
        self.assertEqual(tuple(gr.groups()),
                         ("2016-06-11 - Make a reference to a blog post",
                          "2016/2016-06-11_blogpost_with_label"))

    def test_tocdelay1(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        if sys.version_info[0] == 2:
            warnings.warn(
                "test_postcontent not run on Python 2.7")
            return

        content = """
                    .. tocdelay::

                        blog/2015/2015-04-05_first_blogpost
                    """.replace("                    ", "")

        try:
            rst2html(content,  # fLOG=fLOG,
                               layout="sphinx",
                               writer="rst", keep_warnings=True)
        except ValueError as e:
            self.assertIn("No found document", str(e))

    def test_tocdelay2(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        if sys.version_info[0] == 2:
            warnings.warn(
                "test_postcontent not run on Python 2.7", UserWarning)
            return

        path = os.path.abspath(os.path.dirname(__file__))
        path = os.path.join(path, "data", "blog")
        content = """
                    .. tocdelay::
                        :path: {0}

                        2015/2015-04-05_first_blogpost
                    """.replace("                    ", "").format(path)

        try:
            rst2html(content,  # fLOG=fLOG,
                     layout="sphinx",
                     writer="rst", keep_warnings=True)
        except KeyError as e:
            self.assertIn(
                "Unable to find doctree for '/2015/2015-04-05_first_bl", str(e))

    def test_tocdelay3(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        if sys.version_info[0] == 2:
            warnings.warn(
                "test_postcontent not run on Python 2.7", UserWarning)
            return

        temp = get_temp_folder(__file__, "temp_tocdelay3")
        path = os.path.abspath(os.path.dirname(__file__))
        path = os.path.join(path, "data", "blog")
        content = """
                    .. tocdelay::
                        :path: {0}

                        2015/2015-04-05_first_blogpost
                    """.replace("                    ", "").format(path)

        try:
            rst2rst_folder(content, temp)
        except KeyError as e:
            self.assertIn(
                "Unable to find doctree for '/2015/2015-04-05_first_bl", str(e))


if __name__ == "__main__":
    unittest.main()
