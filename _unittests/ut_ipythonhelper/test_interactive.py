"""
@brief      test log(time=14s)
"""

import sys
import os
import unittest
import numpy as np

from pyquickhelper.loghelper import fLOG
from pyquickhelper.ipythonhelper import StaticInteract, RangeWidget, RadioWidget, DropDownWidget
from pyquickhelper.pycode import fix_tkinter_issues_virtualenv, ExtTestCase


class TestInteractive(ExtTestCase):

    def test_interactive_StaticInteract(self):
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
        self.assertNotEmpty(res)
        ht = res.html()
        self.assertNotEmpty(ht)

    def test_interactive2_RadioWidget(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        fix_tkinter_issues_virtualenv(fLOG=fLOG)
        import matplotlib.pyplot as plt

        def plot(amplitude, color, sele):
            fig, ax = plt.subplots(figsize=(4, 3),
                                   subplot_kw={'axisbelow': True})
            ax.grid(color='w', linewidth=2, linestyle='solid')
            x = np.linspace(0, 10, 1000)
            ax.plot(x, amplitude * np.sin(x), color=color,
                    lw=5, alpha=0.4)
            ax.set_xlim(0, 10)
            ax.set_ylim(-1.1, 1.1)
            return fig

        res = StaticInteract(plot,
                             amplitude=RangeWidget(0.1, 0.3, 0.1, default=0.2),
                             color=RadioWidget(
                                 ['blue', 'green'], default='blue'),
                             sele=DropDownWidget(['a', 'b']))
        self.assertNotEmpty(res)
        ht = res.html()
        self.assertNotEmpty(ht)
        plt.close('all')
        fLOG("end")


if __name__ == "__main__":
    unittest.main()
