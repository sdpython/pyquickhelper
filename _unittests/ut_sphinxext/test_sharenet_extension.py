"""
@brief      test log(time=4s)
@author     Xavier Dupre
"""

import sys
import os
import unittest
import warnings
from docutils.parsers.rst import directives

from pyquickhelper.pycode import get_temp_folder
from pyquickhelper.helpgen import rst2html
from pyquickhelper.sphinxext import ShareNetDirective


class TestShareNetExtension(unittest.TestCase):

    def test_post_parse_sn(self):
        directives.register_directive("sharenet", ShareNetDirective)

    def test_sharenet(self):
        content = """
                    test a directive
                    ================

                    before

                    .. sharenet::
                        :facebook: 1
                        :twitter:

                        this code shoud not appear___

                    after

                    this code shoud appear
                    """.replace("                    ", "")
        if sys.version_info[0] >= 3:
            content = content.replace('u"', '"')

        html = rst2html(content,  # fLOG=fLOG,
                        writer="html", keep_warnings=True,
                        directives=None)

        t1 = "this code shoud not appear"
        if t1 in html:
            raise Exception(html)

        t1 = "this code shoud appear"
        if t1 not in html:
            raise Exception(html)

        t1 = "facebook"
        if t1 not in html:
            raise Exception(html)

        t1 = "linkedin"
        if t1 in html:
            raise Exception(html)

        t1 = "function share_icon(divid, text)"
        if t1 not in html:
            raise Exception(html)

        t1 = '<a href="#"'
        if t1 not in html:
            raise Exception(html)

        t1 = '{1}'
        if t1 in html:
            raise Exception(html)

        t1 = "visit_sharenet_node"
        if t1 in html:
            raise Exception(html)

        temp = get_temp_folder(__file__, "temp_sharenet")
        with open(os.path.join(temp, "out_sharenet.html"), "w", encoding="utf8") as f:
            f.write(html)

    def test_sharenet_inline(self):
        content = """
                    test a directive
                    ================

                    abeforea :sharenet:`facebook-linkedin-twitter-20-body` aaftera
                    """.replace("                    ", "")
        if sys.version_info[0] >= 3:
            content = content.replace('u"', '"')

        html = rst2html(content,  # fLOG=fLOG,
                        writer="html", keep_warnings=True,
                        directives=None)

        t1 = "abeforea"
        if t1 not in html:
            raise Exception(html)

        t1 = "aftera"
        if t1 not in html:
            raise Exception(html)

        t1 = "function share_icon(divid, text)"
        if t1 not in html:
            raise Exception(html)

        t1 = '<a href="#"'
        if t1 not in html:
            raise Exception(html)

        t1 = '{1}'
        if t1 in html:
            raise Exception(html)

        t1 = "visit_sharenet_node"
        if t1 in html:
            raise Exception(html)

        temp = get_temp_folder(__file__, "temp_sharenet_inline")
        with open(os.path.join(temp, "out_sharenet.html"), "w", encoding="utf8") as f:
            f.write(html)

    def test_sharenet_inline_rst(self):
        content = """
                    test a directive
                    ================

                    abeforea :sharenet:`facebook-linkedin-twitter-30-body` aaftera
                    """.replace("                    ", "")
        if sys.version_info[0] >= 3:
            content = content.replace('u"', '"')

        html = rst2html(content,  # fLOG=fLOG,
                        writer="rst", keep_warnings=True,
                        directives=None)

        t1 = ":sharenet:`facebook-linkedin-twitter-30-body`"
        if t1 not in html:
            raise Exception(html)

    def test_sharenet_directive_rst(self):
        content = """
                    test a directive
                    ================

                    abeforea

                    .. sharenet::
                        :facebook: 1
                        :linkedin: 2
                        :twitter: 3
                        :head: False

                    aaftera
                    """.replace("                    ", "")
        if sys.version_info[0] >= 3:
            content = content.replace('u"', '"')

        html = rst2html(content,  # fLOG=fLOG,
                        writer="rst", keep_warnings=True,
                        directives=None)

        t1 = ":sharenet:`facebook-linkedin-twitter-20-body`"
        if t1 not in html:
            raise Exception(html)


if __name__ == "__main__":
    unittest.main()
