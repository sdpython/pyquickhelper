"""
@brief      test log(time=4s)
@author     Xavier Dupre
"""
import os
import unittest
from pyquickhelper.pycode import get_temp_folder, ExtTestCase
from pyquickhelper.helpgen import rst2html
from pyquickhelper.sphinxext import CmdRef
from pyquickhelper.sphinxext.sphinx_cmdref_extension import (
    cmdref_node, visit_cmdref_node, depart_cmdref_node)


class TestDocTreeBuilder(ExtTestCase):

    def test_doctree_builder(self):
        from docutils import nodes as skip_

        content = """
                    test a directive
                    ================

                    before

                    .. cmdref::
                        :title: first cmd
                        :tag: crypt
                        :lid: idcmd3
                        :cmd: pyquickhelper.cli.encryption_cli:encrypt

                        this code shoud appear___

                    after
                    """.replace("                    ", "")
        content = content.replace('u"', '"')

        tives = [("cmdref", CmdRef, cmdref_node,
                  visit_cmdref_node, depart_cmdref_node)]

        html = rst2html(content,  # fLOG=fLOG,
                        writer="doctree", keep_warnings=True,
                        directives=tives, extlinks={'issue': ('http://%s', '_issue_')})

        if not isinstance(html, str):
            raise TypeError(type(html))

        temp = get_temp_folder(__file__, "temp_doctree_builder")
        with open(os.path.join(temp, "out_cmdref.html"), "w", encoding="utf8") as f:
            f.write(html)

        t1 = "this code shoud appear"
        if t1 not in html:
            raise Exception(html)
        t1 = "<section ids=['test-a-directive'] names=['test a directive']>"
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

        t1 = "refid='idcmd3'"
        if t1 not in html:
            raise Exception(html)

    def test_doctree_builder_sphinx(self):
        from docutils import nodes as skip_

        content = """
                    test a --helpe
                    ================

                    before

                    .. cmdref::
                        :title: first cmd
                        :tag: freg
                        :lid: id3
                        :cmd: pyquickhelper.cli.encryption_cli:encrypt

                        this code shoud appear___

                    middle

                    .. cmdreflist::
                        :tag: freg
                        :sort: title

                    after
                    """.replace("                    ", "")
        content = content.replace('u"', '"')

        tives = [("cmdref", CmdRef, cmdref_node,
                  visit_cmdref_node, depart_cmdref_node)]

        html = rst2html(content,  # fLOG=fLOG,
                        writer="doctree", keep_warnings=True,
                        directives=tives, layout="sphinx")

        temp = get_temp_folder(__file__, "temp_doctree_builder_sphinx")
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

        t1 = "refid='indexcmdref-freg0'"
        if t1 not in html:
            raise Exception(html)

        t1 = ': <string>, line 7)'
        if t1 not in html:
            raise Exception(html)

    def test_doctree_builder_sphinx_table(self):
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
        content = content.replace('u"', '"')

        tives = [("cmdref", CmdRef, cmdref_node,
                  visit_cmdref_node, depart_cmdref_node)]

        html = rst2html(content,  # fLOG=fLOG,
                        writer="doctree", keep_warnings=True,
                        directives=tives, layout="sphinx")

        temp = get_temp_folder(__file__, "temp_doctree_builder_sphinx")
        with open(os.path.join(temp, "out_cmdref.html"), "w", encoding="utf8") as f:
            f.write(html)

        t1 = "<tgroup cols=2>"
        if t1 not in html:
            raise Exception(html)

        t1 = "--help"
        if t1 not in html:
            raise Exception(html)

        t1 = "<tbody>"
        if t1 not in html:
            raise Exception(html)

    def test_doctree_only(self):
        from docutils import nodes as skip_

        content = """
                    test a directive
                    ================

                    .. only:: html

                        only for html

                    .. only:: doctree

                        not only for doctree

                    """.replace("                    ", "")
        content = content.replace('u"', '"')

        tives = [("cmdref", CmdRef, cmdref_node,
                  visit_cmdref_node, depart_cmdref_node)]

        text = rst2html(content,  # fLOG=fLOG,
                        writer="doctree", keep_warnings=True,
                        directives=tives, extlinks={'issue': ('http://%s', '_issue_')})

        temp = get_temp_folder(__file__, "temp_only")
        with open(os.path.join(temp, "out_cmdref.doctree.txt"), "w", encoding="utf8") as f:
            f.write(text)

        t1 = "not only for doctree"
        if t1 not in text:
            raise Exception(text)
        t1 = "only for html"
        if t1 not in text:
            raise Exception(text)

    def test_doctree_reference(self):
        from docutils import nodes as skip_

        content = """
                    test a directive
                    ================

                    :py:class:`pyquickhelper.sphinxext.sphinx_doctree_builder.DocTreeBuilder`

                    :py:class:`Renamed <pyquickhelper.sphinxext.sphinx_doctree_builder.DocTreeBuilder>`
                    """.replace("                    ", "")
        content = content.replace('u"', '"')

        tives = [("cmdref", CmdRef, cmdref_node,
                  visit_cmdref_node, depart_cmdref_node)]

        text = rst2html(content,  # fLOG=fLOG,
                        writer="doctree", keep_warnings=True, layout='sphinx',
                        directives=tives, extlinks={'issue': ('http://%s', '_issue_')})

        temp = get_temp_folder(__file__, "temp_only")
        with open(os.path.join(temp, "out_cmdref.doctree.txt"), "w", encoding="utf8") as f:
            f.write(text)

        t1 = "pyquickhelper.sphinxext.sphinx_doctree_builder.DocTreeBuilder"
        if t1 not in text:
            raise Exception(text)
        t1 = "Renamed"
        if t1 not in text:
            raise Exception(text)

    def test_doctree_reference2(self):
        from docutils import nodes as skip_

        content = """

                    .. _l-test-ref:

                    test a directive
                    ================

                    :ref:`reftext <l-test-ref>`

                    *italic*

                    :bigger:`ut`

                    :issue:`1`

                    * bul1
                    * bul2

                    ::

                        rawt

                    .. only:: doctree

                        gggg

                    .. only:: latex

                        hhhh

                    .. only:: html

                        jjjj

                    """.replace("                    ", "")
        content = content.replace('u"', '"')

        text = rst2html(content,  # fLOG=fLOG,
                        writer="doctree", keep_warnings=False, layout='sphinx',
                        extlinks={'issue': ('http://%s', '_issue_')})

        self.assertIn("<emphasis>", text)
        self.assertIn("<list_item>", text)
        self.assertIn("<literal_block", text)
        self.assertIn("<bigger_node", text)
        self.assertIn("gggg", text)
        self.assertIn("hhhh", text)
        self.assertIn("jjjj", text)
        temp = get_temp_folder(__file__, "temp_doctree_reference2")
        with open(os.path.join(temp, "out_cmdref.doctree.txt"), "w", encoding="utf8") as f:
            f.write(text)

    def test_doctree_image(self):

        temp = get_temp_folder(__file__, "temp_doctree_image")
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
        content = content.replace('u"', '"')

        try:
            text = rst2html(content,  # fLOG=fLOG,
                            writer="doctree", keep_warnings=False, layout='sphinx',
                            extlinks={'issue': ('http://%s', '_issue_')})
        except Exception as e:
            raise Exception(
                f"Issue with '{img1}' and '{img2}'") from e

        text = text.replace("\r", "")
        self.assertIn('data/image/im.png', text)
        self.assertIn('alternative1', text)
        self.assertIn("alt='alternative2'", text)
        self.assertIn("width='200'", text)
        self.assertNotIn('\n\n', text)
        with open(os.path.join(temp, "out_image.doctree.txt"), "w", encoding="utf8") as f:
            f.write(text)

    def test_doctree_image_target(self):

        temp = get_temp_folder(__file__, "temp_doctree_image_target")
        root = os.path.abspath(os.path.dirname(__file__))
        img1 = os.path.join(root, "data", "image", "im.png")
        content = """
                    .. image:: {0}
                        :target: https://github.com/sdpython
                        :width: 200
                        :alt: alternative1
                    """.replace("                    ", "").format(img1).replace("\\", "/")
        content = content.replace('u"', '"')

        text = rst2html(content,  # fLOG=fLOG,
                        writer="doctree", keep_warnings=False, layout='sphinx',
                        extlinks={'issue': ('http://%s', '_issue_')})

        text = text.replace("\r", "")
        self.assertIn('data/image/im.png', text)
        self.assertIn("alt='alternative1'", text)
        self.assertIn("width='200'", text)
        with open(os.path.join(temp, "out_image.doctree.txt"), "w", encoding="utf8") as f:
            f.write(text)


if __name__ == "__main__":
    unittest.main()
