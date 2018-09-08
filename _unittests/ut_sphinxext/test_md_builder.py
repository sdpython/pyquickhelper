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

from src.pyquickhelper.pycode import get_temp_folder
from src.pyquickhelper.helpgen import rst2html
from src.pyquickhelper.sphinxext import CmdRef
from src.pyquickhelper.sphinxext.sphinx_cmdref_extension import cmdref_node, visit_cmdref_node, depart_cmdref_node


if sys.version_info[0] == 2:
    from codecs import open


class TestMdBuilder(unittest.TestCase):

    def _test_md_builder(self):
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
                        writer="md", keep_warnings=True,
                        directives=tives, extlinks={'issue': ('http://%s', '_issue_')})

        temp = get_temp_folder(__file__, "temp_md_builder")
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

        t1 = "```"
        if t1 not in html:
            raise Exception(html)

        t1 = '-s STATUS, --status STATUS'
        if t1 not in html:
            raise Exception(html)

        t1 = '.. _idcmd3:'
        if t1 in html:
            raise Exception(html)

    def _test_md_builder_sphinx(self):
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
                        writer="md", keep_warnings=True,
                        directives=tives, layout="sphinx")

        temp = get_temp_folder(__file__, "temp_md_builder_sphinx")
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
        if t1 in html:
            raise Exception(html)

        t1 = '([original entry](#indexcmdref-freg0) : <string>, line 7)'
        if t1 not in html:
            raise Exception(html)

    def _test_md_builder_sphinx_table(self):
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
                        writer="md", keep_warnings=True,
                        directives=tives, layout="sphinx")

        temp = get_temp_folder(__file__, "temp_md_builder_sphinx")
        with open(os.path.join(temp, "out_cmdref.html"), "w", encoding="utf8") as f:
            f.write(html)

        t1 = "+--------+----------+"
        if t1 in html:
            raise Exception(html)

        t1 = "--help"
        if t1 not in html:
            raise Exception(html)

        t1 = "a | b1"
        if t1 not in html:
            raise Exception(html)

        spl = html.split("--- | ---")
        if len(spl) > 2:
            raise Exception(html)

    def _test_md_only(self):
        from docutils import nodes as skip_

        content = """
                    test a directive
                    ================

                    .. only:: html

                        only for html

                    .. only:: md

                        only for md

                    """.replace("                    ", "")
        if sys.version_info[0] >= 3:
            content = content.replace('u"', '"')

        tives = [("cmdref", CmdRef, cmdref_node,
                  visit_cmdref_node, depart_cmdref_node)]

        text = rst2html(content,  # fLOG=fLOG,
                        writer="md", keep_warnings=True,
                        directives=tives, extlinks={'issue': ('http://%s', '_issue_')})

        temp = get_temp_folder(__file__, "temp_only")
        with open(os.path.join(temp, "out_cmdref.md"), "w", encoding="utf8") as f:
            f.write(text)

        t1 = "only for md"
        if t1 not in text:
            raise Exception(text)
        t1 = "only for html"
        if t1 in text:
            raise Exception(text)

        text = rst2html(content,  # fLOG=fLOG,
                        writer="html", keep_warnings=True,
                        directives=tives, extlinks={'issue': ('http://%s', '_issue_')})

        temp = get_temp_folder(__file__, "temp_only")
        with open(os.path.join(temp, "out_cmdref.html"), "w", encoding="utf8") as f:
            f.write(text)

        t1 = "only for md"
        if t1 in text:
            raise Exception(text)
        t1 = "only for html"
        if t1 not in text:
            raise Exception(text)

    def _test_md_reference(self):
        from docutils import nodes as skip_

        content = """
                    test a directive
                    ================

                    :py:class:`src.pyquickhelper.sphinxext.sphinx_md_builder.MdBuilder`

                    :py:class:`Renamed <src.pyquickhelper.sphinxext.sphinx_md_builder.MdBuilder>`
                    """.replace("                    ", "")
        if sys.version_info[0] >= 3:
            content = content.replace('u"', '"')

        tives = [("cmdref", CmdRef, cmdref_node,
                  visit_cmdref_node, depart_cmdref_node)]

        text = rst2html(content,  # fLOG=fLOG,
                        writer="md", keep_warnings=True, layout='sphinx',
                        directives=tives, extlinks={'issue': ('http://%s', '_issue_')})

        temp = get_temp_folder(__file__, "temp_only")
        with open(os.path.join(temp, "out_cmdref.md"), "w", encoding="utf8") as f:
            f.write(text)

        t1 = "src.pyquickhelper.sphinxext.sphinx_md_builder.MdBuilder"
        if t1 not in text:
            raise Exception(text)
        t1 = "Renamed"
        if t1 not in text:
            raise Exception(text)
        t1 = "[Renamed]"
        if t1 not in text:
            raise Exception(text)

    def test_md_reference2(self):
        from docutils import nodes as skip_

        content = """

                    .. _l-test-ref:

                    test a directive
                    ================

                    :ref:`reftext <l-test-ref>`

                    :keyword:`ggg`

                    :py:exc:`ggg`

                    *italic*

                    :bigger:`ut`

                    :issue:`1`

                    * bul1
                    * bul2

                    ::

                        rawt

                    .. only:: md

                        gggg

                    .. only:: latex

                        hhhh

                    .. only:: html

                        jjjj

                    """.replace("                    ", "")
        if sys.version_info[0] >= 3:
            content = content.replace('u"', '"')

        text = rst2html(content,  # fLOG=fLOG,
                        writer="md", keep_warnings=False, layout='sphinx',
                        extlinks={'issue': ('http://%s', '_issue_')})

        self.assertIn("*italic*", text)
        self.assertIn("* bul1", text)
        self.assertIn("```", text)
        self.assertIn("**ut**", text)
        self.assertIn("gggg", text)
        self.assertNotIn("hhhh", text)
        self.assertNotIn("jjjj", text)
        self.assertNotIn("SYSTEM", text)
        temp = get_temp_folder(__file__, "temp_only")
        with open(os.path.join(temp, "out_cmdref.md"), "w", encoding="utf8") as f:
            f.write(text)


if __name__ == "__main__":
    unittest.main()
