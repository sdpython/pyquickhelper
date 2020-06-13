"""
@brief      test log(time=4s)
@author     Xavier Dupre
"""

import sys
import os
import unittest
import warnings
from docutils.parsers.rst import directives
from sphinx.errors import ExtensionError
from pyquickhelper.pycode import get_temp_folder
from pyquickhelper.helpgen import rst2html, rst2rst_folder
from pyquickhelper.sphinxext import TocDelayDirective


class TestTocDelayExtension(unittest.TestCase):

    def test_post_parse(self):
        directives.register_directive("tocdelay", TocDelayDirective)

    def test_regex(self):
        s = "2016-06-11 - Make a reference to a blog post <2016/2016-06-11_blogpost_with_label>"
        reg = TocDelayDirective.regex_title
        gr = reg.search(s)
        self.assertTrue(gr is not None)
        self.assertEqual(tuple(gr.groups()),
                         ("2016-06-11 - Make a reference to a blog post",
                          "2016/2016-06-11_blogpost_with_label"))

    def test_tocdelay1(self):
        content = """
                    .. tocdelay::

                        blog/2015/2015-04-05_first_blogpost
                    """.replace("                    ", "")

        try:
            rst2html(content, layout="sphinx",
                     writer="rst", keep_warnings=True)
        except ValueError as e:
            self.assertIn("No found document", str(e))

    def test_tocdelay2(self):
        path = os.path.abspath(os.path.dirname(__file__))
        path = os.path.join(path, "data", "blog")
        content = """
                    .. tocdelay::
                        :path: {0}

                        2015/2015-04-05_first_blogpost
                    """.replace("                    ", "").format(path)

        try:
            rst2html(content, layout="sphinx",
                     writer="rst", keep_warnings=True)
        except (KeyError, ExtensionError) as e:
            self.assertIn(
                "event 'doctree-resolved' threw an exception", str(e))

    def test_tocdelay3(self):
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
        except (KeyError, ExtensionError) as e:            
            self.assertIn(
                "event 'doctree-resolved' threw an exception", str(e))


if __name__ == "__main__":
    unittest.main()
