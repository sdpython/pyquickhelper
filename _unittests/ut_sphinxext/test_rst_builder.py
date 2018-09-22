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
from src.pyquickhelper.sphinxext.sphinximages.sphinxtrib.images import ImageDirective


if sys.version_info[0] == 2:
    from codecs import open


class TestRstBuilder(ExtTestCase):

    def test_rst_builder(self):
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

    def test_rst_only(self):
        from docutils import nodes as skip_

        content = """
                    test a directive
                    ================

                    .. only:: html

                        only for html

                    .. only:: rst

                        only for rst

                    """.replace("                    ", "")
        if sys.version_info[0] >= 3:
            content = content.replace('u"', '"')

        tives = [("cmdref", CmdRef, cmdref_node,
                  visit_cmdref_node, depart_cmdref_node)]

        text = rst2html(content,  # fLOG=fLOG,
                        writer="rst", keep_warnings=True,
                        directives=tives, extlinks={'issue': ('http://%s', '_issue_')})

        temp = get_temp_folder(__file__, "temp_only")
        with open(os.path.join(temp, "out_cmdref.rst"), "w", encoding="utf8") as f:
            f.write(text)

        t1 = "only for rst"
        if t1 not in text:
            raise Exception(text)
        t1 = "only for html"
        if t1 in text:
            raise Exception(text)

        text = rst2html(content,  # fLOG=fLOG,
                        writer="html", keep_warnings=True,
                        directives=tives, extlinks={'issue': ('http://%s', '_issue_')})

        temp = get_temp_folder(__file__, "temp_only")
        with open(os.path.join(temp, "out_cmdref.rst"), "w", encoding="utf8") as f:
            f.write(text)

        t1 = "only for rst"
        if t1 in text:
            raise Exception(text)
        t1 = "only for html"
        if t1 not in text:
            raise Exception(text)

    def test_rst_reference(self):
        from docutils import nodes as skip_

        content = """
                    test a directive
                    ================

                    :py:class:`src.pyquickhelper.sphinxext.sphinx_rst_builder.RstBuilder`

                    :py:class:`Renamed <src.pyquickhelper.sphinxext.sphinx_rst_builder.RstBuilder>`
                    """.replace("                    ", "")
        if sys.version_info[0] >= 3:
            content = content.replace('u"', '"')

        tives = [("cmdref", CmdRef, cmdref_node,
                  visit_cmdref_node, depart_cmdref_node)]

        text = rst2html(content,  # fLOG=fLOG,
                        writer="rst", keep_warnings=True, layout='sphinx',
                        directives=tives, extlinks={'issue': ('http://%s', '_issue_')})

        temp = get_temp_folder(__file__, "temp_only")
        with open(os.path.join(temp, "out_cmdref.rst"), "w", encoding="utf8") as f:
            f.write(text)

        t1 = "src.pyquickhelper.sphinxext.sphinx_rst_builder.RstBuilder"
        if t1 not in text:
            raise Exception(text)
        t1 = ":py:class:`Renamed"
        if t1 not in text:
            raise Exception(text)

        text = rst2html(content,  # fLOG=fLOG,
                        writer="html", keep_warnings=True, layout='sphinx',
                        directives=tives, extlinks={'issue': ('http://%s', '_issue_')})

        temp = get_temp_folder(__file__, "temp_only")
        with open(os.path.join(temp, "out_cmdref.rst"), "w", encoding="utf8") as f:
            f.write(text)

        t1 = "src.pyquickhelper.sphinxext.sphinx_rst_builder.RstBuilder"
        if t1 not in text:
            raise Exception(text)
        t1 = "<p>Renamed</p>"
        if t1 not in text:
            raise Exception(text)

    def test_rst_reference2(self):
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

                    .. only:: rst

                        gggg

                    .. only:: latex

                        hhhh

                    .. only:: html

                        jjjj

                    """.replace("                    ", "")
        if sys.version_info[0] >= 3:
            content = content.replace('u"', '"')

        text = rst2html(content,  # fLOG=fLOG,
                        writer="rst", keep_warnings=False, layout='sphinx',
                        extlinks={'issue': ('http://%s', '_issue_')})

        self.assertIn("*italic*", text)
        self.assertIn("* bul1", text)
        self.assertIn("::", text)
        self.assertIn(":bigger:`ut`", text)
        self.assertIn("gggg", text)
        self.assertNotIn("hhhh", text)
        self.assertNotIn("jjjj", text)
        temp = get_temp_folder(__file__, "temp_rst_reference2")
        with open(os.path.join(temp, "out_cmdref.rst"), "w", encoding="utf8") as f:
            f.write(text)

    def test_rst_image(self):
        temp = get_temp_folder(__file__, "temp_rst_image")
        root = os.path.abspath(os.path.dirname(__file__))
        img1 = os.path.join(root, "data", "image", "im.png")
        img2 = os.path.join(root, "data", "thumbnail", "im.png")
        content = """
                    .. image:: {0}
                        :width: 200
                        :alt: alternative1
                        :download: True

                    * .. image:: {1}
                        :width: 200
                        :alt: alternative2
                        :download: True
                    """.replace("                    ", "").format(img1, img2).replace("\\", "/")
        if sys.version_info[0] >= 3:
            content = content.replace('u"', '"')

        tives = [("image", ImageDirective)]

        try:
            text = rst2html(content,  # fLOG=fLOG,
                            writer="rst", keep_warnings=False, layout='sphinx',
                            extlinks={'issue': ('http://%s', '_issue_')},
                            directives=tives, rst_image_dest=temp)
        except Exception as e:
            raise Exception(
                "Issue with '{0}' and '{1}'".format(img1, img2)) from e

        text = text.replace("\r", "")
        self.assertNotIn('unknown option: "download"', text)
        self.assertIn(':: 5cf2985161e8ba56d893.png', text)
        self.assertIn('   :download: True', text)
        self.assertIn('   :alt: alternative1', text)
        self.assertIn('      :alt: alternative2', text)
        self.assertIn('      :width: 200', text)
        self.assertNotIn('\n\n', text)
        self.assertExists(os.path.join(temp, '5cf2985161e8ba56d893.png'))
        with open(os.path.join(temp, "out_image.rst"), "w", encoding="utf8") as f:
            f.write(text)

    def test_rst_image_target(self):

        temp = get_temp_folder(__file__, "temp_rst_image_target")
        root = os.path.abspath(os.path.dirname(__file__))
        img1 = os.path.join(root, "data", "image", "im.png")
        content = """
                    .. image:: {0}
                        :target: https://github.com/sdpython.png
                        :width: 200
                        :alt: alternative1
                    """.replace("                    ", "").format(img1).replace("\\", "/")
        if sys.version_info[0] >= 3:
            content = content.replace('u"', '"')

        text = rst2html(content,  # fLOG=fLOG,
                        writer="rst", keep_warnings=False, layout='sphinx',
                        extlinks={'issue': ('http://%s', '_issue_')})

        text = text.replace("\r", "")
        self.assertIn('data/image/im.png', text)
        self.assertIn('   :alt: alternative1', text)
        self.assertIn('   :width: 200', text)
        with open(os.path.join(temp, "out_image.rst"), "w", encoding="utf8") as f:
            f.write(text)

    def test_rst_image_target2(self):

        temp = get_temp_folder(__file__, "temp_rst_image_target2")
        root = os.path.abspath(os.path.dirname(__file__))
        img1 = os.path.join(root, "data", "image", "im.png")
        content = """
                    .. image:: {0}
                        :target: https://github.com/sdpython.png
                        :width: 200
                        :alt: alternative1
                    """.replace("                    ", "").format(img1).replace("\\", "/")
        if sys.version_info[0] >= 3:
            content = content.replace('u"', '"')

        text = rst2html(content,  # fLOG=fLOG,
                        writer="rst", keep_warnings=False, layout='sphinx',
                        extlinks={'issue': ('http://%s', '_issue_')},
                        rst_image_dest=temp)

        text = text.replace("\r", "")
        self.assertNotIn('data/image/im.png', text)
        self.assertIn('   :alt: alternative1', text)
        self.assertIn('   :width: 200', text)
        with open(os.path.join(temp, "out_image.rst"), "w", encoding="utf8") as f:
            f.write(text)


if __name__ == "__main__":
    unittest.main()
