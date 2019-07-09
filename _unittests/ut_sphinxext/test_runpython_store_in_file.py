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
from pyquickhelper.pycode import ExtTestCase, get_temp_folder
from pyquickhelper.sphinxext.sphinx_runpython_extension import RunPythonDirective


class TestRunPythonStoreInFile(ExtTestCase):

    def test_runpython_store_in_file(self):

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
                        :process:
                        :store_in_file: __DEST__

                        import math
                        import inspect

                        def fctfct():
                            return math.pi

                        code = inspect.getsource(fctfct)
                        print("***********")
                        print(code)
                        print("***********")
                    """.replace("                    ", "")

        temp = get_temp_folder(__file__, "temp_runpython_store_in_file")
        dest = os.path.join(temp, "exescript.py")
        content = content.replace('__DEST__', dest)
        tives = [("runpythonthis", RunPythonThisDirective, runpythonthis_node,
                  visit_rp_node, depart_rp_node)]

        rst = rst2html(content, writer="rst", keep_warnings=True,
                       directives=tives)
        self.assertIn("def fctfct():", rst)
        self.assertIn("return math.pi", rst)
        self.assertExists(dest)


if __name__ == "__main__":
    unittest.main()
