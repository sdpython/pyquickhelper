"""
@brief      test log(time=4s)
@author     Xavier Dupre
"""
import os
import unittest
import warnings
from datetime import datetime
from pyquickhelper.pycode import get_temp_folder, ExtTestCase
from pyquickhelper.helpgen import rst2html
from pyquickhelper.sphinxext import gitlog_role
from docutils.parsers.rst.roles import register_canonical_role


class TestGitlogExtension(ExtTestCase):

    def test_post_parse_sn(self):
        register_canonical_role("gitlog", gitlog_role)

    def test_gitlog(self):
        from docutils import nodes as skip_

        content = """
                    test a directive
                    ================

                    before

                    :gitlog:`date`

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

        t1 = str(datetime.now().year)
        if t1 not in html:
            raise Exception(html)

        temp = get_temp_folder(__file__, "temp_gitlog")
        with open(os.path.join(temp, "out_gitlog.html"), "w", encoding="utf8") as f:
            f.write(html)

    def test_gitlog_inline(self):
        from docutils import nodes as skip_

        content = """
                    test a directive
                    ================

                    abeforea :gitlog:`date:{0}` aaftera
                    """.replace("                    ", "")
        this = os.path.abspath(__file__).replace('.pyc', '.py')
        content = content.format(this).replace('\\', '/')
        content = content.replace("_gitlog", "_bigger")

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

        t1 = "date:"
        if t1 in html:
            raise Exception(html)

        t1 = "bigger"
        if t1 in html:
            raise Exception(html)

        temp = get_temp_folder(__file__, "temp_gitlog_inline")
        with open(os.path.join(temp, "out_gitlog.html"), "w", encoding="utf8") as f:
            f.write(html)


if __name__ == "__main__":
    unittest.main()
