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
from src.pyquickhelper.pycode import get_temp_folder, ExtTestCase, skipif_azure_macosx
from src.pyquickhelper.helpgen import rst2html
from src.pyquickhelper.sphinxext import RunPythonDirective


class TestRunPythonExtensionImage(ExtTestCase):

    def test_post_parse(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        directives.register_directive("runpython", RunPythonDirective)

    @skipif_azure_macosx("Terminating app due to uncaught exception 'NSInvalidArgumentException'")
    def test_runpython_image(self):
        """
        this test also test the extension runpython
        """
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        from docutils import nodes

        class runpythonthis_node(nodes.Structural, nodes.Element):
            pass

        class RunPythonThisDirective (RunPythonDirective):
            runpython_class = runpythonthis_node

        def visit_rp_node(self, node):
            self.body.append("<p><b>visit_rp_node</b></p>")

        def depart_rp_node(self, node):
            self.body.append("<p><b>depart_rp_node</b></p>")

        if "enable_disabled_documented_pieces_of_code" in sys.__dict__:
            raise Exception("this case shoud not be")

        temp = get_temp_folder(__file__, "temp_runpython_image")
        content = """
                    test a directive
                    ================

                    .. runpythonthis::
                        :rst:
                        :showcode:

                        import matplotlib.pyplot as plt
                        fig, ax = plt.subplots(1, 1, figsize=(4, 4))
                        ax.plot([0, 1], [0, 1], '--')
                        if __WD__ is None:
                            raise Exception(__WD__)
                        fig.savefig("__FOLD__/oo.png")

                        text = ".. image:: oo.png\\n    :width: 200px"
                        print(text)

                    """.replace("                    ", "").replace("__FOLD__", temp.replace("\\", "/"))
        if sys.version_info[0] >= 3:
            content = content.replace('u"', '"')

        tives = [("runpythonthis", RunPythonThisDirective, runpythonthis_node,
                  visit_rp_node, depart_rp_node)]

        html = rst2html(content,  # fLOG=fLOG,
                        writer="custom", keep_warnings=True,
                        directives=tives)

        with open(os.path.join(temp, "out.html"), "w", encoding="utf8") as f:
            f.write(html)
        img = os.path.join(temp, "oo.png")
        self.assertExists(img)


if __name__ == "__main__":
    unittest.main()
