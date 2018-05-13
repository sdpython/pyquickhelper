# -*- coding: utf-8 -*-
"""
@brief      test tree node (time=1s)
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
from src.pyquickhelper.pycode import get_temp_folder
from src.pyquickhelper.texthelper.html_helper import html_in_frame


class TestHtmlHelper(unittest.TestCase):

    def test_src_import(self):
        """for pylint"""
        self.assertTrue(src is not None)

    def test_html_in_frame(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        ht = html_in_frame("<h1>title</h1>")
        body = "<html><body>" + ht + "</body></html>"
        self.assertIn("data:text/html;base64,PGgxPnRpdGxlPC9oMT4=", ht)
        temp = get_temp_folder(__file__, "temp_html_in_frame")
        tempf = os.path.join(temp, "out.html")
        with open(tempf, "w") as f:
            f.write(body)


if __name__ == "__main__":
    unittest.main()
