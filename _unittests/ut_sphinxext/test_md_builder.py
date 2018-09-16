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

from src.pyquickhelper.pycode import get_temp_folder, ExtTestCase
from src.pyquickhelper.helpgen import rst2html
from src.pyquickhelper.sphinxext import CmdRef
from src.pyquickhelper.sphinxext.sphinx_cmdref_extension import cmdref_node, visit_cmdref_node, depart_cmdref_node


if sys.version_info[0] == 2:
    from codecs import open


class TestMdBuilder(ExtTestCase):

    def test_md_builder(self):
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

    def test_md_builder_sphinx(self):
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

    def test_md_builder_sphinx_table(self):
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

    def test_md_only(self):
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

    def test_md_reference(self):
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

    def test_md_title(self):
        from docutils import nodes as skip_

        content = """

                    title1
                    ======

                    title2
                    ======

                    title3
                    ++++++

                    title4
                    ******

                    """.replace("                    ", "")
        if sys.version_info[0] >= 3:
            content = content.replace('u"', '"')

        text = rst2html(content,  # fLOG=fLOG,
                        writer="md", keep_warnings=False, layout='sphinx',
                        extlinks={'issue': ('http://%s', '_issue_')})

        self.assertIn("# title1", text)
        self.assertIn("# title2", text)
        self.assertIn("## title3", text)
        self.assertIn("### title4", text)
        temp = get_temp_folder(__file__, "temp_md_title")
        with open(os.path.join(temp, "out_md_title.md"), "w", encoding="utf8") as f:
            f.write(text)

    def test_md_image(self):

        temp = get_temp_folder(__file__, "temp_md_image")
        root = os.path.abspath(os.path.dirname(__file__))
        img1 = os.path.join(root, "data", "image", "im.png")
        img2 = os.path.join(root, "data", "thumbnail", "im.png")
        content = """
                    .. image:: {0}
                        :width: 200
                        :alt: alternative1

                    * .. image:: {1}
                        :width: 200
                        :alt: alternative2
                    """.replace("                    ", "").format(img1, img2).replace("\\", "/")
        if sys.version_info[0] >= 3:
            content = content.replace('u"', '"')

        text = rst2html(content,  # fLOG=fLOG,
                        writer="md", keep_warnings=False, layout='sphinx',
                        extlinks={'issue': ('http://%s', '_issue_')},
                        md_image_dest=temp)

        text = text.replace("\r", "")
        self.assertIn('![alternative1]', text)
        self.assertIn('![alternative2]', text)
        self.assertIn('=200x', text)
        self.assertNotIn('\n\n', text)
        self.assertIn("![alternative1](5cf2985161e8ba56d893.png =200x)", text)
        self.assertExists(os.path.join(temp, '5cf2985161e8ba56d893.png'))
        with open(os.path.join(temp, "md_image.md"), "w", encoding="utf8") as f:
            f.write(text)

    def test_md_image_target(self):

        temp = get_temp_folder(__file__, "temp_md_image_target")
        root = os.path.abspath(os.path.dirname(__file__))
        img1 = os.path.join(root, "data", "image", "im.png")
        content = """
                    .. image:: {0}
                        :target: https://github.com/sdpython
                        :width: 200
                        :alt: alternative1
                    """.replace("                    ", "").format(img1).replace("\\", "/")
        if sys.version_info[0] >= 3:
            content = content.replace('u"', '"')

        text = rst2html(content,  # fLOG=fLOG,
                        writer="md", keep_warnings=False, layout='sphinx',
                        extlinks={'issue': ('http://%s', '_issue_')},
                        md_image_dest=temp)

        text = text.replace("\r", "")
        self.assertIn('![alternative1]', text)
        self.assertIn('=200x', text)
        self.assertIn("![alternative1](5cf2985161e8ba56d893.png =200x)", text)
        self.assertExists(os.path.join(temp, '5cf2985161e8ba56d893.png'))
        with open(os.path.join(temp, "md_image.md"), "w", encoding="utf8") as f:
            f.write(text)


if __name__ == "__main__":
    unittest.main()
