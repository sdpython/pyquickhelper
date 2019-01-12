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

from src.pyquickhelper.loghelper.flog import fLOG
from src.pyquickhelper.helpgen import rst2html


class TestRst2HtmlBug(unittest.TestCase):

    def test_src_import(self):
        """for pylint"""
        self.assertTrue(src is not None)

    def test_rst2html_bug_faq(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        content = """
                        .. faqref::
                            :title: How to add a FAQ?
                            :tag: faqexample2

                            Some description.

                        .. faqreflist::
                            :tag: faqexample2
                            :contents:
        """.replace("                        ", "")

        text = rst2html(content, writer="rst", layout="sphinx")
        if "(`original entry <#indexfaqref-faqexample20>`_ : <string>, line 2)" not in text:
            raise Exception(text)


if __name__ == "__main__":
    unittest.main()
