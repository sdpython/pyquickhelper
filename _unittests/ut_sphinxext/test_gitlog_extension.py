"""
@brief      test log(time=4s)
@author     Xavier Dupre
"""

import sys
import os
import unittest
import warnings
from datetime import datetime

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
from src.pyquickhelper.sphinxext import gitlog_role
from docutils.parsers.rst.roles import register_canonical_role


class TestGitlogExtension(unittest.TestCase):

    def _test_post_parse_sn(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        register_canonical_role("gitlog", gitlog_role)

    def test_gitlog(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        from docutils import nodes as skip_

        content = """
                    test a directive
                    ================

                    before

                    :gitlog:`date`

                    after

                    this code shoud appear
                    """.replace("                    ", "")
        if sys.version_info[0] >= 3:
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
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

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
