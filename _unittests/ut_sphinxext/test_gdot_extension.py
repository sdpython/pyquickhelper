"""
@brief      test log(time=4s)
@author     Xavier Dupre
"""
import os
import unittest
import logging
from docutils.parsers.rst import directives
from pyquickhelper.pycode import get_temp_folder, ExtTestCase, skipif_appveyor
from pyquickhelper.helpgen import rst2html


class TestGDotExtension(ExtTestCase):

    def setUp(self):
        logger = logging.getLogger('gdot')
        logger.disabled = True

    @skipif_appveyor("logging issue")
    def test_gdot1(self):
        content = """
                    before

                    .. gdot::

                        digraph foo {
                          "bar" -> "baz";
                        }

                    after
                    """.replace("                    ", "")

        content = rst2html(content, writer="rst", keep_warnings=True)
        self.assertIn('digraphfoo{"bar"->"baz";}',
                      content.replace("\n", "").replace(" ", ""))

    @skipif_appveyor("logging issue")
    def test_gdot2(self):
        content = """
                    before

                    .. gdot::
                        :script:

                        print('''digraph foo { HbarH -> HbazH; }'''.replace("H", '"'))

                    after
                    """.replace("                    ", "")

        content = rst2html(content, writer="rst", keep_warnings=True)
        self.assertIn('digraph foo { "bar" -> "baz"; }', content)

    @skipif_appveyor("logging issue")
    def test_gdot2_split(self):
        content = """
                    before

                    .. gdot::
                        :script: BEGIN

                        print('''...BEGINdigraph foo { HbarH -> HbazH; }'''.replace("H", '"'))

                    after
                    """.replace("                    ", "")

        content = rst2html(content, writer="rst", keep_warnings=True)
        self.assertIn('digraph foo { "bar" -> "baz"; }', content)
        self.assertNotIn('BEGIN', content)

    @skipif_appveyor("logging issue")
    def test_gdot3_svg(self):
        content = """
                    before

                    .. gdot::
                        :format: svg

                        digraph foo {
                          "bar" -> "baz";
                        }

                    after
                    """.replace("                    ", "")

        content = rst2html(content, writer="html", keep_warnings=True)
        self.assertIn("document.getElementById('gdot-", content)
        self.assertIn('foo {\\n  \\"bar\\" -> \\"baz\\";\\n}");', content)

    @skipif_appveyor("logging issue")
    def test_gdot3_svg_process(self):
        content = """
                    before

                    .. gdot::
                        :format: svg
                        :process:

                        digraph foo {
                          "bar" -> "baz";
                        }

                    after
                    """.replace("                    ", "")

        content = rst2html(content, writer="html", keep_warnings=True)
        self.assertIn("document.getElementById('gdot-", content)
        self.assertIn('foo {\\n  \\"bar\\" -> \\"baz\\";\\n}");', content)

    @skipif_appveyor("logging issue")
    def test_gdot4_png(self):
        content = """
                    before

                    .. gdot::
                        :format: png

                        digraph foo {
                          "bar" -> "baz";
                        }

                    after
                    """.replace("                    ", "")

        try:
            content = rst2html(content, writer="html", keep_warnings=True)
        except FileNotFoundError:
            # This class cannot write on disk.
            return
        self.assertIn("png", content)


if __name__ == "__main__":
    unittest.main()
