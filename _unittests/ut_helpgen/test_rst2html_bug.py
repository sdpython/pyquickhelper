"""
@brief      test log(time=8s)
@author     Xavier Dupre
"""

import sys
import os
import unittest

from pyquickhelper.loghelper.flog import fLOG
from pyquickhelper.helpgen import rst2html


class TestRst2HtmlBug(unittest.TestCase):

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
            raise AssertionError(text)


if __name__ == "__main__":
    unittest.main()
