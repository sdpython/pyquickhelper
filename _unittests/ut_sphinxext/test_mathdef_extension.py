"""
@brief      test log(time=4s)
@author     Xavier Dupre
"""

import sys
import os
import unittest
from docutils.parsers.rst import directives

from pyquickhelper.loghelper.flog import fLOG
from pyquickhelper.pycode import get_temp_folder
from pyquickhelper.helpgen import rst2html
from pyquickhelper.sphinxext import MathDef, MathDefList
from pyquickhelper.sphinxext.sphinx_mathdef_extension import mathdef_node, visit_mathdef_node, depart_mathdef_node


class TestMathDefExtension(unittest.TestCase):

    def test_post_parse_sn_todoext(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        directives.register_directive("mathdef", MathDef)
        directives.register_directive("mathdeflist", MathDefList)

    def test_mathdef(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        from docutils import nodes as skip_

        content = """
                    test a directive
                    ================

                    before

                    .. mathdef::
                        :title: first def
                        :tag: definition
                        :lid: label1

                        this code should appear___

                    after
                    """.replace("                    ", "")
        if sys.version_info[0] >= 3:
            content = content.replace('u"', '"')

        tives = [("mathdef", MathDef, mathdef_node,
                  visit_mathdef_node, depart_mathdef_node)]

        html = rst2html(content,  # fLOG=fLOG,
                        writer="custom", keep_warnings=True,
                        directives=tives, extlinks={'issue': ('http://%s', '_issue_')})

        temp = get_temp_folder(__file__, "temp_mathdef", clean=False)
        with open(os.path.join(temp, "test_mathdef.html"), "w", encoding="utf8") as f:
            f.write(html)

        t1 = "this code should appear"
        if t1 not in html:
            raise Exception(html)

        t1 = "after"
        if t1 not in html:
            raise Exception(html)

        t1 = "first def"
        if t1 not in html:
            raise Exception(html)

    def test_mathdeflist(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        from docutils import nodes as skip_

        content = """
                    test a directive
                    ================

                    before

                    .. mathdef::
                        :title: first def2
                        :tag: Theoreme

                        this code should appear___

                    middle

                    .. mathdeflist::
                        :tag: definition

                    after
                    """.replace("                    ", "")
        if sys.version_info[0] >= 3:
            content = content.replace('u"', '"')

        tives = [("mathdef", MathDef, mathdef_node,
                  visit_mathdef_node, depart_mathdef_node)]

        html = rst2html(content,  # fLOG=fLOG,
                        writer="custom", keep_warnings=True,
                        directives=tives)

        temp = get_temp_folder(__file__, "temp_mathdef", clean=False)
        with open(os.path.join(temp, "test_mathdeflist.html"), "w", encoding="utf8") as f:
            f.write(html)

        t1 = "this code should appear"
        if t1 not in html:
            raise Exception(html)

        t1 = "after"
        if t1 not in html:
            raise Exception(html)

        t1 = "first def2"
        if t1 not in html:
            raise Exception(html)

    def test_mathdeflist_contents(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        from docutils import nodes as skip_

        content = """
                    test a directive
                    ================

                    before

                    .. mathdef::
                        :title: first def2
                        :tag: Theoreme

                        this code should appear___

                    middle

                    .. mathdeflist::
                        :tag: definition
                        :contents:

                    after
                    """.replace("                    ", "")
        if sys.version_info[0] >= 3:
            content = content.replace('u"', '"')

        tives = [("mathdef", MathDef, mathdef_node,
                  visit_mathdef_node, depart_mathdef_node)]

        html = rst2html(content,  # fLOG=fLOG,
                        writer="custom", keep_warnings=True,
                        directives=tives)

        temp = get_temp_folder(__file__, "temp_mathdef", clean=False)
        with open(os.path.join(temp, "test_mathdeflist_contents.html"), "w", encoding="utf8") as f:
            f.write(html)

        t1 = "this code should appear"
        if t1 not in html:
            raise Exception(html)

        t1 = "after"
        if t1 not in html:
            raise Exception(html)

        t1 = "first def2"
        if t1 not in html:
            raise Exception(html)

    def test_mathdeflist_contents_body_sphinx(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        from docutils import nodes as skip_

        content = """
                    test a directive
                    ================

                    before

                    .. mathdef::
                        :title: first def2
                        :tag: Theoreme

                        this code should appear___

                    middle

                    .. mathdeflist::
                        :tag: definition
                        :contents:

                    middle2

                    .. mathdeflist::
                        :tag: Theoreme
                        :contents:

                    after
                    """.replace("                    ", "")
        if sys.version_info[0] >= 3:
            content = content.replace('u"', '"')

        tives = [("mathdef", MathDef, mathdef_node,
                  visit_mathdef_node, depart_mathdef_node)]

        html = rst2html(content,  # fLOG=fLOG,
                        writer="custom", keep_warnings=True,
                        directives=tives, layout="sphinx")

        body = rst2html(content,  # fLOG=fLOG,
                        writer="custom", keep_warnings=True,
                        directives=tives, layout="sphinx_body")
        if "<body>" in body:
            raise Exception(body)
        if "</body>" in body:
            raise Exception(body)

        temp = get_temp_folder(__file__, "temp_mathdef", clean=False)
        with open(os.path.join(temp, "test_mathdeflist_contents_sphinx.html"), "w", encoding="utf8") as f:
            f.write(html)

        # not yet ready

        if "alabaster" in html:
            raise Exception(html)

        t1 = "this code should appear"
        if t1 not in body:
            raise Exception(body)

        t1 = "after"
        if t1 not in body:
            raise Exception(body)

        t1 = "first def2"
        if t1 not in body:
            raise Exception(body)

        t1 = 'class="reference internal"'
        if t1 not in body:
            raise Exception(body)


if __name__ == "__main__":
    unittest.main()
