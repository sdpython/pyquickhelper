"""
@brief      test log(time=4s)
@author     Xavier Dupre
"""
import os
import unittest
from docutils.parsers.rst import directives
from pyquickhelper.pycode import get_temp_folder, ExtTestCase, skipif_appveyor
from pyquickhelper.helpgen import rst2html
from pyquickhelper.sphinxext import NbRef, NbRefList
from pyquickhelper.sphinxext.sphinx_nbref_extension import (
    nbref_node, visit_nbref_node, depart_nbref_node)


class TestNbRefExtension(ExtTestCase):

    def test_post_parse_nbref(self):
        directives.register_directive("nbref", NbRef)
        directives.register_directive("nbreflist", NbRefList)

    @skipif_appveyor("logging issue")
    def test_nbref(self):
        from docutils import nodes as skip_

        content = """
                    test a directive
                    ================

                    before

                    .. nbref::
                        :title: first todo
                        :tag: bug
                        :lid: id3

                        this code shoud appear___

                    after
                    """.replace("                    ", "")
        content = content.replace('u"', '"')

        tives = [("nbref", NbRef, nbref_node,
                  visit_nbref_node, depart_nbref_node)]

        html = rst2html(content,  # fLOG=fLOG,
                        writer="custom", keep_warnings=True,
                        directives=tives, extlinks={'issue': ('http://%s', '_issue_')})

        temp = get_temp_folder(__file__, "temp_nbref")
        with open(os.path.join(temp, "out_nbref.html"), "w", encoding="utf8") as f:
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

    @skipif_appveyor("logging issue")
    def test_nbreflist(self):
        from docutils import nodes as skip_

        content = """
                    test a directive
                    ================

                    before

                    .. nbref::
                        :title: first todo
                        :tag: freg
                        :lid: id3

                        this code shoud appear___

                    middle

                    .. nbreflist::
                        :tag: freg
                        :sort: title

                    after
                    """.replace("                    ", "")
        content = content.replace('u"', '"')

        tives = [("nbref", NbRef, nbref_node,
                  visit_nbref_node, depart_nbref_node)]

        html = rst2html(content,  # fLOG=fLOG,
                        writer="custom", keep_warnings=True,
                        directives=tives, layout="sphinx")
        if "admonition-nbref nbref_node admonition" not in html:
            raise html

        temp = get_temp_folder(__file__, "temp_nbreflist")
        with open(os.path.join(temp, "out_nbref.html"), "w", encoding="utf8") as f:
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
