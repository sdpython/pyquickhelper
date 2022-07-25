"""
@brief      test log(time=4s)
@author     Xavier Dupre
"""
import sys
import os
import unittest
import warnings
from docutils.parsers.rst import directives
from pyquickhelper.pycode import get_temp_folder, ExtTestCase
from pyquickhelper.helpgen import rst2html
from pyquickhelper.sphinxext import RunPythonDirective


class TestRunPythonExtensionToggle(ExtTestCase):

    def test_post_parse(self):
        directives.register_directive("runpython", RunPythonDirective)

    def test_runpython_toggle(self):
        """
        this test also test the extension runpython
        """
        from docutils import nodes

        class runpythonthis_node(nodes.Structural, nodes.Element):
            pass

        class RunPythonThisDirective (RunPythonDirective):
            runpython_class = runpythonthis_node

        def visit_rp_node(self, node):
            if hasattr(self, 'body'):
                self.body.append("<p><b>visit_rp_node</b></p>")
            else:
                self.add_text(".. beginrunpython." + self.nl)

        def depart_rp_node(self, node):
            "local function"
            if hasattr(self, 'body'):
                self.body.append("<p><b>depart_rp_node</b></p>")
            else:
                self.add_text(".. endrunpython." + self.nl)

        if "enable_disabled_documented_pieces_of_code" in sys.__dict__:
            raise Exception("this case shoud not be")

        content = """
                    test a directive
                    ================

                    .. runpythonthis::
                        :setsysvar:
                        :rst:
                        :showcode:
                        :toggle: both

                        print(u"this code shoud appear" + u"___")
                        import sys
                        print(u"setsysvar: " + str(sys.__dict__.get('enable_disabled_documented_pieces_of_code', None)))
                    """.replace("                    ", "")
        content = content.replace('u"', '"')

        tives = [("runpythonthis", RunPythonThisDirective, runpythonthis_node,
                  visit_rp_node, depart_rp_node)]
        temp = get_temp_folder(__file__, "temp_runpython_toggle")

        # HTML
        html = rst2html(content,  # fLOG=fLOG,
                        writer="custom", keep_warnings=True,
                        directives=tives)

        t1 = "button"
        if t1 not in html:
            raise Exception(html)
        with open(os.path.join(temp, "out.html"), "w", encoding="utf8") as f:
            f.write(html)

        # RST
        html = rst2html(content,  # fLOG=fLOG,
                        writer="rst", keep_warnings=True,
                        directives=tives)

        t1 = "<<<::"
        t2 = "<<<.. code-block:: python"
        if t1 not in html and t2 not in html:
            raise Exception(html)
        t1 = ".. collapse::"
        if t1 not in html:
            raise Exception(html)
        with open(os.path.join(temp, "out.rst"), "w", encoding="utf8") as f:
            f.write(html)


if __name__ == "__main__":
    unittest.main()
