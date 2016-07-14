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
from src.pyquickhelper.sphinxext import FaqRef, FaqRefList
from src.pyquickhelper.sphinxext.sphinx_faqref_extension import faqref_node, visit_faqref_node, depart_faqref_node


if sys.version_info[0] == 2:
    from codecs import open


class TestFaqRefExtension(unittest.TestCase):

    def test_post_parse_faqref(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        directives.register_directive("faqref", FaqRef)
        directives.register_directive("faqreflist", FaqRefList)

    def test_faqre(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

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
        if sys.version_info[0] >= 3:
            content = content.replace('u"', '"')

        tives = [("faqref", FaqRef, faqref_node,
                  visit_faqref_node, depart_faqref_node)]

        html = rst2html(content, fLOG=fLOG,
                        writer="custom", keep_warnings=True,
                        directives=tives, extlinks={'issue': ('http://%s', '_issue_')})

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

    def test_faqreflist(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

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
        if sys.version_info[0] >= 3:
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
