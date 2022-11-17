"""
@brief      test log(time=2s)
"""

import sys
import os
import warnings
from textwrap import dedent
import unittest

from pyquickhelper.pycode import (
    ExtTestCase, skipif_travis, skipif_circleci, get_temp_folder)
from pyquickhelper.helpgen.graphviz_helper import plot_graphviz


class TestHelpGenGraphvizHelper(ExtTestCase):

    @skipif_travis('graphviz is not installed')
    @skipif_circleci('graphviz is not installed')
    @skipif_appveyor("Message: 'generated new fontManager'")
    def test_plot_graphviz(self):
        dot = dedent("""
        digraph D {
          A [shape=diamond]
          B [shape=box]
          C [shape=circle]

          A -> B [style=dashed, color=grey]
          A -> C [color="black:invis:black"]
          A -> D [penwidth=5, arrowhead=none]
        }
        """)
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(1, 1)
        try:
            plot_graphviz(dot, ax=ax)
        except FileNotFoundError as e:
            if "No such file or directory: 'dot'" in str(e):
                warnings.warn(f"graphviz not installed: {e!r}.")
                return
        plt.close('all')

    @skipif_travis('graphviz is not installed')
    @skipif_circleci('graphviz is not installed')
    @skipif_appveyor("Message: 'generated new fontManager'")
    def test_plot_graphviz_temp(self):
        dot = dedent("""
        digraph D {
          A [shape=diamond]
          B [shape=box]
          C [shape=circle]

          A -> B [style=dashed, color=grey]
          A -> C [color="black:invis:black"]
          A -> D [penwidth=5, arrowhead=none]
        }
        """)
        import matplotlib.pyplot as plt
        temp = get_temp_folder(__file__, "temp_plot_graphviz_temp")
        img = os.path.join(temp, "dot.png")
        dotf = os.path.join(temp, "dot.dot")
        fig, ax = plt.subplots(1, 1)
        try:
            plot_graphviz(dot, ax=ax, temp_dot=dotf, temp_img=img)
        except FileNotFoundError as e:
            if "No such file or directory: 'dot'" in str(e):
                warnings.warn(f"graphviz not installed: {e!r}.")
                return
        plt.close('all')
        self.assertExists(dotf)
        self.assertExists(img)


if __name__ == "__main__":
    unittest.main()
