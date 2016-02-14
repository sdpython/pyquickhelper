"""
@brief      test log(time=4s)
@author     Xavier Dupre
"""

import sys
import os
import unittest
import sphinx
import warnings
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
from src.pyquickhelper import get_temp_folder
from src.pyquickhelper.helpgen.utils_sphinx_doc import private_migrating_doxygen_doc
from src.pyquickhelper.helpgen import BlogPost, BlogPostList, BlogPostDirective, BlogPostDirectiveAgg
from src.pyquickhelper.helpgen import rst2html
from src.pyquickhelper.helpgen import ShareNetDirective, sharenet_node
from src.pyquickhelper.helpgen.sphinx_sharenet_extension import visit_sharenet_node, depart_sharenet_node

if sys.version_info[0] == 2:
    from codecs import open


class TestShareNetExtension(unittest.TestCase):

    def test_post_parse_sn(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        directives.register_directive("sharenet", ShareNetDirective)

    def test_sharenet(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        if sys.version_info[0] == 2:
            warnings.warn(
                "test_sharenet not run on Python 2.7")
            return

        from docutils import nodes

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

        html = rst2html(content, fLOG=fLOG,
                        writer="custom", keep_warnings=True,
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
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        if sys.version_info[0] == 2:
            warnings.warn(
                "test_sharenet not run on Python 2.7")
            return

        from docutils import nodes

        content = """
                    test a directive
                    ================

                    abeforea :sharenet:`facebook-linkedin-twitter-20-body` aaftera
                    """.replace("                    ", "")
        if sys.version_info[0] >= 3:
            content = content.replace('u"', '"')

        html = rst2html(content, fLOG=fLOG,
                        writer="custom", keep_warnings=True,
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


if __name__ == "__main__":
    unittest.main()
