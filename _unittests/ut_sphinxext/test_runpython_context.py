"""
@brief      test log(time=4s)
@author     Xavier Dupre
"""

import sys
import os
import unittest
import warnings
from docutils.parsers.rst import directives

from pyquickhelper.helpgen import rst2html
from pyquickhelper.pycode import ExtTestCase
from pyquickhelper.sphinxext.sphinx_runpython_extension import RunPythonDirective


class TestRunPythoncontext(ExtTestCase):

    def test_runpython_context(self):

        from docutils import nodes

        class runpythonthis_node(nodes.Structural, nodes.Element):
            pass

        class RunPythonThisDirective(RunPythonDirective):
            runpython_class = runpythonthis_node

        def visit_rp_node(self, node):
            self.add_text("<p><b>visit_rp_node</b></p>")

        def depart_rp_node(self, node):
            self.add_text("<p><b>depart_rp_node</b></p>")

        content = """
                    test a directive
                    ================

                    .. runpythonthis::
                        :showcode:
                        :store:

                        magic_store = "saved for later"

                    .. runpythonthis::
                        :restore:

                        a = 5
                        try:
                            print("restored", magic_store)
                        except Exception as e:
                            print("failed")
                            for k, v in sorted(locals().copy().items()):
                                print(k, "=", [v])
                    """.replace("                    ", "")

        tives = [("runpythonthis", RunPythonThisDirective, runpythonthis_node,
                  visit_rp_node, depart_rp_node)]

        rst = rst2html(content, writer="rst", keep_warnings=True,
                       directives=tives)
        self.assertIn("restored saved for later", rst)
        self.assertNotIn("failed", rst)


if __name__ == "__main__":
    unittest.main()
