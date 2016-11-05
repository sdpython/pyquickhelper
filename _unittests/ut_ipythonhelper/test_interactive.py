"""
@brief      test log(time=14s)
"""

import sys
import os
import unittest
import numpy as np
import matplotlib.pyplot as plt

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
from src.pyquickhelper.ipythonhelper import StaticInteract, RangeWidget, RadioWidget


class TestInteractive(unittest.TestCase):

    def test_interactive1(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        def show_fib(N):
            sequence = ""
            a, b = 0, 1
            for i in range(N):
                sequence += "{0} ".format(a)
                a, b = b, a + b
            return sequence

        res = StaticInteract(show_fib,
                             N=RangeWidget(1, 100, default=10))
        assert res is not None

    def test_interactive2(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        def plot(amplitude, color):
            fig, ax = plt.subplots(figsize=(4, 3),
                                   subplot_kw={'axisbg': '#EEEEEE',
                                               'axisbelow': True})
            ax.grid(color='w', linewidth=2, linestyle='solid')
            x = np.linspace(0, 10, 1000)
            ax.plot(x, amplitude * np.sin(x), color=color,
                    lw=5, alpha=0.4)
            ax.set_xlim(0, 10)
            ax.set_ylim(-1.1, 1.1)
            return fig

        res = StaticInteract(plot,
                             amplitude=RangeWidget(0.1, 0.3, 0.1, default=0.2),
                             color=RadioWidget(['blue', 'green'], default='blue'))
        assert res is not None


if __name__ == "__main__":
    unittest.main()
