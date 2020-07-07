"""
@brief      test log(time=2s)
"""

import sys
import os
from textwrap import dedent
import unittest

from pyquickhelper.pycode import ExtTestCase, skipif_travis, skipif_circleci
from pyquickhelper.helpgen.graphviz_helper import plot_graphviz


class TestHelpGenGraphvizHelper(ExtTestCase):

    @skipif_travis('graphviz is not installed')
    @skipif_circleci('graphviz is not installed')
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
        plot_graphviz(dot, ax=ax)
        plt.close('all')


if __name__ == "__main__":
    unittest.main()
