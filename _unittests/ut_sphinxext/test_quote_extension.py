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

from src.pyquickhelper.pycode import get_temp_folder
from src.pyquickhelper.helpgen import rst2html
from src.pyquickhelper.sphinxext import QuoteNode
from src.pyquickhelper.sphinxext.sphinx_quote_extension import quote_node, visit_quote_node, depart_quote_node


if sys.version_info[0] == 2:
    from codecs import open


class TestMathDefExtension(unittest.TestCase):

    def test_post_parse_sn_todoext(self):
        directives.register_directive("quote", QuoteNode)

    def test_quote(self):
        from docutils import nodes as skip_

        content = """
                    .. quote::
                        :author: auteur
                        :book: livre titre
                        :lid: label1
                        :pages: 234
                        :year: 2018

                        this code should appear___
                    """.replace("                    ", "")
        if sys.version_info[0] >= 3:
            content = content.replace('u"', '"')

        tives = [("quote", QuoteNode, quote_node,
                  visit_quote_node, depart_quote_node)]

        html = rst2html(content,  # fLOG=fLOG,
                        writer="html", keep_warnings=True,
                        directives=tives, extlinks={'issue': ('http://%s', '_issue_')})

        temp = get_temp_folder(__file__, "temp_quote", clean=False)
        with open(os.path.join(temp, "test_quote.html"), "w", encoding="utf8") as f:
            f.write(html)

        t1 = "this code should appear"
        if t1 not in html:
            raise Exception(html)
        if "auteur" not in html:
            raise Exception(html)
        if "livre titre" not in html:
            raise Exception(html)
        if "234" not in html:
            raise Exception(html)
        if "2018" not in html:
            raise Exception(html)

        rst = rst2html(content,  # fLOG=fLOG,
                       writer="rst", keep_warnings=True,
                       directives=tives, extlinks={'issue': ('http://%s', '_issue_')})

        with open(os.path.join(temp, "test_quote.rst"), "w", encoding="utf8") as f:
            f.write(rst)

        t1 = "this code should appear"
        if t1 not in rst:
            raise Exception(rst)
        if "auteur" not in rst:
            raise Exception(rst)
        if "livre titre" not in rst:
            raise Exception(rst)
        if "234" not in rst:
            raise Exception(rst)
        if "2018" not in rst:
            raise Exception(rst)


if __name__ == "__main__":
    unittest.main()
