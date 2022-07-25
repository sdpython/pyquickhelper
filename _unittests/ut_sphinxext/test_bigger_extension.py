"""
@brief      test log(time=4s)
@author     Xavier Dupre
"""
import os
import unittest
import warnings
from pyquickhelper.pycode import get_temp_folder, ignore_warnings
from pyquickhelper.helpgen import rst2html
from pyquickhelper.sphinxext import bigger_role
from docutils.parsers.rst.roles import register_canonical_role


class TestBiggerExtension(unittest.TestCase):

    @ignore_warnings(PendingDeprecationWarning)
    def test_post_parse_sn(self):
        register_canonical_role("bigger", bigger_role)

    @ignore_warnings(PendingDeprecationWarning)
    def test_bigger(self):
        from docutils import nodes as skip_

        content = """
                    test a directive
                    ================

                    before

                    :bigger:`facebook`

                    after

                    this code shoud appear
                    """.replace("                    ", "")
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

        t1 = '{1}'
        if t1 in html:
            raise Exception(html)

        t1 = "visit_sharenet_node"
        if t1 in html:
            raise Exception(html)

        temp = get_temp_folder(__file__, "temp_bigger")
        with open(os.path.join(temp, "out_bigger.html"), "w", encoding="utf8") as f:
            f.write(html)

    @ignore_warnings(PendingDeprecationWarning)
    def test_bigger_inline(self):
        from docutils import nodes as skip_

        content = """
                    test a directive
                    ================

                    abeforea :bigger:`facebook` aaftera
                    """.replace("                    ", "")
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

        t1 = '{1}'
        if t1 in html:
            raise Exception(html)

        t1 = '<font size="4">facebook</font>'
        if t1 not in html:
            raise Exception(html)

        t1 = "visit_sharenet_node"
        if t1 in html:
            raise Exception(html)

        temp = get_temp_folder(__file__, "temp_bigger_inline")
        with open(os.path.join(temp, "out_bigger.html"), "w", encoding="utf8") as f:
            f.write(html)


if __name__ == "__main__":
    unittest.main()
