"""
@brief      test log(time=9s)
"""

import sys
import os
import unittest

from pyquickhelper.pycode import get_temp_folder
from pyquickhelper.loghelper import fLOG
from pyquickhelper.ipythonhelper.run_notebook import notebook_coverage, badge_notebook_coverage


class TestNotebookReportBadge(unittest.TestCase):

    def test_notebook_report_badge(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        temp = get_temp_folder(__file__, "temp_notebook_report_badge")
        data = os.path.join(temp, "..", "data",
                            "dump.notebook.pyquickhelper.txt")
        df = notebook_coverage(os.path.dirname(data), data)
        img = os.path.join(temp, "badge-notebook.png")
        imgs = [img]
        badge_notebook_coverage(df, img)
        self.assertTrue(os.path.exists(img))
        df['nbcell'] = 1
        df['nbvalid'] = 1
        df['nbrun'] = 1
        img = os.path.join(temp, "badge-notebook2.png")
        badge_notebook_coverage(df, img)
        self.assertTrue(os.path.exists(img))
        imgs.append(img)

        data = os.path.dirname(data)
        exp = [os.path.join(data, "badge-notebook.png"),
               os.path.join(data, "badge-notebook2.png")]
        for img, exp in zip(imgs, exp):
            with open(img, "rb") as f:
                c1 = f.read()
            with open(exp, "rb") as f:
                c2 = f.read()
            if c1 != c2:
                raise AssertionError(
                    f"Difference in '{img}' and '{exp}'")


if __name__ == "__main__":
    unittest.main()
