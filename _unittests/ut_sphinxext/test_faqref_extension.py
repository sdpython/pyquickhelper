"""
@brief      test log(time=4s)
@author     Xavier Dupre
"""
import os
import unittest
from docutils.parsers.rst import directives
from pyquickhelper.loghelper.flog import fLOG
from pyquickhelper.pycode import (
    get_temp_folder, ExtTestCase, ignore_warnings, skipif_appveyor)
from pyquickhelper.helpgen import rst2html
from pyquickhelper.sphinxext import FaqRef, FaqRefList
from pyquickhelper.sphinxext.sphinx_faqref_extension import (
    faqref_node, visit_faqref_node, depart_faqref_node)


class TestFaqRefExtension(ExtTestCase):

    @ignore_warnings(PendingDeprecationWarning)
    def test_post_parse_faqref(self):
        directives.register_directive("faqref", FaqRef)
        directives.register_directive("faqreflist", FaqRefList)

    @ignore_warnings(PendingDeprecationWarning)
    @skipif_appveyor("logging error")
    def test_faqref(self):
        from docutils import nodes as skip_

        content = """
                    test a directive
                    ================

                    before

                    .. faqref::
                        :title: first todo
                        :tag: bug
                        :lid: id3

                        this code shoud appear___

                    after
                    """.replace("                    ", "")
        content = content.replace('u"', '"')

        tives = [("faqref", FaqRef, faqref_node,
                  visit_faqref_node, depart_faqref_node)]

        html = rst2html(content, fLOG=fLOG,
                        writer="custom", keep_warnings=True,
                        directives=tives, extlinks={'issue': ('http://%s', '_issue_%s')})

        temp = get_temp_folder(__file__, "temp_faqref")
        with open(os.path.join(temp, "out_faqref.html"), "w", encoding="utf8") as f:
            f.write(html)

        t1 = "this code shoud appear"
        if t1 not in html:
            raise Exception(html)

        t1 = "after"
        if t1 not in html:
            raise Exception(html)

        t1 = "first todo"
        if t1 not in html:
            raise Exception(html)

    @ignore_warnings(PendingDeprecationWarning)
    @skipif_appveyor("logging error")
    def test_faqreflist(self):
        from docutils import nodes as skip_

        content = """
                    test a directive
                    ================

                    before

                    .. faqref::
                        :title: first todo
                        :tag: freg
                        :lid: id3

                        this code shoud appear___

                    middle

                    .. faqreflist::
                        :tag: freg
                        :sort: title

                    after
                    """.replace("                    ", "")
        content = content.replace('u"', '"')

        tives = [("faqref", FaqRef, faqref_node,
                  visit_faqref_node, depart_faqref_node)]

        html = rst2html(content, fLOG=fLOG,
                        writer="custom", keep_warnings=True,
                        directives=tives)
        if "admonition-faqref faqref_node admonition" not in html:
            raise html

        temp = get_temp_folder(__file__, "temp_faqreflist")
        with open(os.path.join(temp, "out_faqref.html"), "w", encoding="utf8") as f:
            f.write(html)

        t1 = "this code shoud appear"
        if t1 not in html:
            raise Exception(html)

        t1 = "after"
        if t1 not in html:
            raise Exception(html)

        t1 = "first todo"
        if t1 not in html:
            raise Exception(html)


if __name__ == "__main__":
    unittest.main()
