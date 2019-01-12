"""
@brief      test log(time=4s)
@author     Xavier Dupre
"""

import sys
import os
import unittest
import warnings

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
from src.pyquickhelper.helpgen import rst2html


class TestBokehExtension(unittest.TestCase):

    def test_bokeh(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        from docutils import nodes as skip_
        from src.pyquickhelper.sphinxext.bokeh.bokeh_plot import BokehPlotDirective
        self.assertTrue(BokehPlotDirective is not None)

        content = """
                    =======
                    History
                    =======

                    "this code should appear

                    .. bokeh-plot::

                        from bokeh.plotting import figure, output_file, show

                        output_file("temp_unittest.html")

                        x = [1, 2, 3, 4, 5]
                        y = [6, 7, 6, 4, 5]

                        p = figure(title="example_bokeh", plot_width=300, plot_height=300)
                        p.line(x, y, line_width=2)
                        p.circle(x, y, size=10, fill_color="white")

                        show(p)

                    """.replace("                    ", "")
        if sys.version_info[0] >= 3:
            content = content.replace('u"', '"')

        html = rst2html(content,  # fLOG=fLOG,
                        writer="html", keep_warnings=True,
                        directives=None, layout="sphinx")

        t1 = "this code should appear"
        if t1 not in html:
            raise Exception(html)

        temp = get_temp_folder(__file__, "temp_bokeh_extension")
        with open(os.path.join(temp, "page_bokeh.html"), "w", encoding="utf-8") as f:
            f.write(html)

        if 'Unknown directive type' in html:
            raise Exception(html)

        if '<<string>>#document-<<string>>' in html:
            pass
        else:
            raise Exception(html)

        if 'bokeh-plot-string-inline' not in html:
            raise Exception(html)


if __name__ == "__main__":
    unittest.main()
