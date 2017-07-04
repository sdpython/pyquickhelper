"""
@brief      test log(time=4s)
@author     Xavier Dupre
"""

import sys
import os
import unittest
from docutils.parsers.rst import directives

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
from src.pyquickhelper.pycode import get_temp_folder
from src.pyquickhelper.helpgen import rst2html
from src.pyquickhelper.sphinxext import MathDef, MathDefList
from src.pyquickhelper.sphinxext.sphinx_mathdef_extension import mathdef_node, visit_mathdef_node, depart_mathdef_node


if sys.version_info[0] == 2:
    from codecs import open


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

        temp = get_temp_folder(__file__, "temp_mathdef")
        with open(os.path.join(temp, "out_mathdef.html"), "w", encoding="utf8") as f:
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

                        this code shoud appear___

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

        temp = get_temp_folder(__file__, "temp_mathdeflist")
        with open(os.path.join(temp, "out_mathdef.html"), "w", encoding="utf8") as f:
            f.write(html)

        t1 = "this code shoud appear"
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

                        this code shoud appear___

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

        temp = get_temp_folder(__file__, "temp_mathdeflist_contents")
        with open(os.path.join(temp, "out_mathdef_contents.html"), "w", encoding="utf8") as f:
            f.write(html)

        t1 = "this code shoud appear"
        if t1 not in html:
            raise Exception(html)

        t1 = "after"
        if t1 not in html:
            raise Exception(html)

        t1 = "first def2"
        if t1 not in html:
            raise Exception(html)


if __name__ == "__main__":
    unittest.main()
