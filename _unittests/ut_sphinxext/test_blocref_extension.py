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
from src.pyquickhelper.sphinxext import BlocRef, BlocRefList
from src.pyquickhelper.sphinxext.sphinx_blocref_extension import blocref_node, visit_blocref_node, depart_blocref_node


if sys.version_info[0] == 2:
    from codecs import open


class TestBlocRefExtension(unittest.TestCase):

    def test_post_parse_blocref(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        directives.register_directive("blocref", BlocRef)
        directives.register_directive("blocreflist", BlocRefList)

    def test_blocref(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        from docutils import nodes as skip_

        content = """
                    test a directive
                    ================

                    before

                    .. blocref::
                        :title: first todo
                        :tag: bug
                        :lid: id3

                        this code shoud appear___

                    after
                    """.replace("                    ", "")
        if sys.version_info[0] >= 3:
            content = content.replace('u"', '"')

        tives = [("blocref", BlocRef, blocref_node,
                  visit_blocref_node, depart_blocref_node)]

        html = rst2html(content, fLOG=fLOG,
                        writer="custom", keep_warnings=True,
                        directives=tives, extlinks={'issue': ('http://%s', '_issue_')})

        temp = get_temp_folder(__file__, "temp_blocref")
        with open(os.path.join(temp, "out_blocref.html"), "w", encoding="utf8") as f:
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

    def test_blocref2(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        from docutils import nodes as skip_

        content = """
                    test a directive
                    ================

                    before

                    .. blocref::
                        :title: first todo
                        :tag: bug
                        :label: id3

                        this code shoud appear___

                    after
                    """.replace("                    ", "")
        if sys.version_info[0] >= 3:
            content = content.replace('u"', '"')

        tives = [("blocref", BlocRef, blocref_node,
                  visit_blocref_node, depart_blocref_node)]

        html = rst2html(content, fLOG=fLOG,
                        writer="custom", keep_warnings=True,
                        directives=tives, extlinks={'issue': ('http://%s', '_issue_')})

        temp = get_temp_folder(__file__, "temp_blocref")
        with open(os.path.join(temp, "out_blocref.html"), "w", encoding="utf8") as f:
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

    def test_blocreflist(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        from docutils import nodes as skip_

        content = """
                    test a directive
                    ================

                    before

                    .. blocref::
                        :title: first todo
                        :tag: freg
                        :lid: id3

                        this code shoud appear___

                    middle

                    .. blocreflist::
                        :tag: freg
                        :sort: title
                        :contents: 1

                    after
                    """.replace("                    ", "")
        if sys.version_info[0] >= 3:
            content = content.replace('u"', '"')

        tives = [("blocref", BlocRef, blocref_node,
                  visit_blocref_node, depart_blocref_node)]

        html = rst2html(content, fLOG=fLOG,
                        writer="custom", keep_warnings=True,
                        directives=tives)

        temp = get_temp_folder(__file__, "temp_blocreflist")
        with open(os.path.join(temp, "out_blocref.html"), "w", encoding="utf8") as f:
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
