"""
@brief      test log(time=8s)
@author     Xavier Dupre
"""

import sys
import os
import unittest
import warnings

from pyquickhelper.loghelper import fLOG
from pyquickhelper.pycode import get_temp_folder
from pyquickhelper.filehelper import create_visual_diff_through_html_files


class TestVisualDiff(unittest.TestCase):

    def test_visual_diff(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        temp = get_temp_folder(__file__, "temp_visual_diff")
        page = os.path.join(temp, "page_diff.html")

        f = __file__.replace(".pyc", ".py")
        try:
            diff = create_visual_diff_through_html_files(f, f, page=page)
        except FileNotFoundError as e:
            try:
                import pymyinstall as skip_
                raise e
            except ImportError:
                return

        fLOG(page)
        assert os.path.exists(page)
        assert len(diff) > 0
        with open(page, "r", encoding="utf8") as f:
            content = f.read()

        if '"diff' + 'view.js"' in content:
            raise AssertionError("no related path:\n##\n" + content + "\n##")
        assert "<body>" in content
        assert "<html>" in content
        assert '<div id="diffoutput"> </div>' in content

    def test_visual_diff_notebook(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        try:
            import IPython as skip_
        except ImportError:
            warnings.warn("IPython is missing, cannot run that test")
            return

        f = __file__.replace(".pyc", ".py")
        try:
            html, js = create_visual_diff_through_html_files(
                f, f, notebook=True)
        except FileNotFoundError as e:
            try:
                import pymyinstall as skip___
                raise e
            except ImportError:
                return

        from IPython.core.display import HTML, Javascript
        assert isinstance(html, HTML)
        assert isinstance(js, Javascript)


if __name__ == "__main__":
    unittest.main()
