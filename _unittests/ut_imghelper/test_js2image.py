"""
@brief      test log(time=7s)

skip this test for regular run
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


from src.pyquickhelper.loghelper import fLOG
from src.pyquickhelper.pycode import ExtTestCase
from src.pyquickhelper.imghelper.js_helper import run_js_fct


class TestJs2Image(ExtTestCase):

    def test_js2fct(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        script = 'function add(a, b) {return a + b}'
        fct = run_js_fct(script)
        c = fct(3, 4)
        self.assertEqual(c, 7)

    @unittest.skip('not implemented yet')
    def test_js2fctdom(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        script = """
              var svgGraph = Viz("digraph{ a-> b; a-> c -> d;}");
              document.getElementById('mygraph').innerHTML = svgGraph;
              """
        fct = run_js_fct(
            script, required="http://www.xavierdupre.fr/js/vizjs/viz")
        c = fct("")
        assert c


if __name__ == "__main__":
    unittest.main()
