"""
@brief      test log(time=4s)
@author     Xavier Dupre
"""

import sys
import os
import unittest

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
from src.pyquickhelper.sphinxext import CmdRef
from src.pyquickhelper.sphinxext.sphinx_cmdref_extension import cmdref_node, visit_cmdref_node, depart_cmdref_node


if sys.version_info[0] == 2:
    from codecs import open


class TestRstBuilder(unittest.TestCase):

    def test_rst_builder(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        from docutils import nodes as skip_

        content = """
                    test a directive
                    ================

                    before

                    .. cmdref::
                        :title: first cmd
                        :tag: crypt
                        :lid: idcmd3
                        :cmd: src.pyquickhelper.cli.encryption_cli:encrypt

                        this code shoud appear___

                    after
                    """.replace("                    ", "")
        if sys.version_info[0] >= 3:
            content = content.replace('u"', '"')

        tives = [("cmdref", CmdRef, cmdref_node,
                  visit_cmdref_node, depart_cmdref_node)]

        html = rst2html(content,  # fLOG=fLOG,
                        writer="rst", keep_warnings=True,
                        directives=tives, extlinks={'issue': ('http://%s', '_issue_')})

        temp = get_temp_folder(__file__, "temp_rst_builder")
        with open(os.path.join(temp, "out_cmdref.html"), "w", encoding="utf8") as f:
            f.write(html)

        t1 = "this code shoud appear"
        if t1 not in html:
            raise Exception(html)
        t1 = "before"
        if t1 not in html:
            raise Exception(html)

        t1 = "after"
        if t1 not in html:
            raise Exception(html)

        t1 = "before"
        if t1 not in html:
            raise Exception(html)

        t1 = "--help"
        if t1 not in html:
            raise Exception(html)

        t1 = '-s STATUS, --status STATUS'
        if t1 not in html:
            raise Exception(html)

        t1 = '.. _idcmd3:'
        if t1 not in html:
            raise Exception(html)

    def test_rst_builder_sphinx(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        from docutils import nodes as skip_

        content = """
                    test a --helpe
                    ================

                    before

                    .. cmdref::
                        :title: first cmd
                        :tag: freg
                        :lid: id3
                        :cmd: src.pyquickhelper.cli.encryption_cli:encrypt

                        this code shoud appear___

                    middle

                    .. cmdreflist::
                        :tag: freg
                        :sort: title

                    after
                    """.replace("                    ", "")
        if sys.version_info[0] >= 3:
            content = content.replace('u"', '"')

        tives = [("cmdref", CmdRef, cmdref_node,
                  visit_cmdref_node, depart_cmdref_node)]

        html = rst2html(content,  # fLOG=fLOG,
                        writer="rst", keep_warnings=True,
                        directives=tives, layout="sphinx")

        temp = get_temp_folder(__file__, "temp_rst_builder_sphinx")
        with open(os.path.join(temp, "out_cmdref.html"), "w", encoding="utf8") as f:
            f.write(html)

        t1 = "this code shoud appear"
        if t1 not in html:
            raise Exception(html)

        t1 = "--help"
        if t1 not in html:
            raise Exception(html)

        t1 = ' -s STATUS, --status STATUS'
        if t1 not in html:
            raise Exception(html)

        t1 = '.. _indexcmdreflistlist-0:'
        if t1 not in html:
            raise Exception(html)

        t1 = '(`original entry <#indexcmdref-freg0>`_ : <string>, line 7)'
        if t1 not in html:
            raise Exception(html)

    def test_rst_builder_sphinx_table(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        from docutils import nodes as skip_

        content = """
                    test a --helpe
                    ================

                    before

                    +------+--------+
                    | a    | b1     |
                    +------+--------+
                    | a    | b2     |
                    +------+--------+

                    .. list-table::
                        :widths: 5 6
                        :header-rows: 1

                        * - h1
                          - h2
                        * - a1
                          - b1
                        * - d2
                          - e2

                    after
                    """.replace("                    ", "")
        if sys.version_info[0] >= 3:
            content = content.replace('u"', '"')

        tives = [("cmdref", CmdRef, cmdref_node,
                  visit_cmdref_node, depart_cmdref_node)]

        html = rst2html(content,  # fLOG=fLOG,
                        writer="rst", keep_warnings=True,
                        directives=tives, layout="sphinx")

        temp = get_temp_folder(__file__, "temp_rst_builder_sphinx")
        with open(os.path.join(temp, "out_cmdref.html"), "w", encoding="utf8") as f:
            f.write(html)

        t1 = "+--------+----------+"
        if t1 not in html:
            raise Exception(html)

        t1 = "--help"
        if t1 not in html:
            raise Exception(html)

        t1 = "+=======+========+"
        if t1 not in html:
            raise Exception(html)


if __name__ == "__main__":
    unittest.main()
