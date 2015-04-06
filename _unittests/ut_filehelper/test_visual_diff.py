"""
@brief      test log(time=8s)
@author     Xavier Dupre
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

from src.pyquickhelper import fLOG, get_temp_folder
from src.pyquickhelper import create_visual_diff_through_html_files


class TestVisualDiff(unittest.TestCase):

    def test_visual_diff(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        temp = get_temp_folder(__file__, "temp_visual_diff")
        page = os.path.join(temp, "page_diff.html")

        f = __file__.replace(".pyc", ".py")
        diff = create_visual_diff_through_html_files(f, f, page=page)
        fLOG(page)
        assert os.path.exists(page)
        assert len(diff) > 0


if __name__ == "__main__":
    unittest.main()
