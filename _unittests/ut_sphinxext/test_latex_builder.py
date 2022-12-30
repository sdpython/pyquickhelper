"""
@brief      test log(time=4s)
@author     Xavier Dupre
"""
import os
import unittest
from pyquickhelper.pycode import get_temp_folder, ExtTestCase
from pyquickhelper.helpgen import rst2html
from pyquickhelper.sphinxext import CmdRef
from pyquickhelper.sphinxext.sphinx_cmdref_extension import cmdref_node, visit_cmdref_node, depart_cmdref_node


class TestLatexBuilder(ExtTestCase):

    def test_latex_builder(self):
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

        tives = [("cmdref", CmdRef, cmdref_node,
                  visit_cmdref_node, depart_cmdref_node)]

        html = rst2html(content,  # fLOG=fLOG,
                        writer="elatex", keep_warnings=True,
                        directives=tives, extlinks={'issue': ('http://%s', '_issue_%s')})

        temp = get_temp_folder(__file__, "temp_latex_builder")
        with open(os.path.join(temp, "out_cmdref.tex"), "w", encoding="utf8") as f:
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

        t1 = "\\PYGZhy{}"
        if t1 not in html:
            raise Exception(html)

        t1 = "sphinxVerbatim"
        if t1 not in html:
            raise Exception(html)

    def test_latex_builder_sphinx(self):
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
                        writer="elatex", keep_warnings=True,
                        directives=tives, layout="sphinx")

        temp = get_temp_folder(__file__, "temp_latex_builder_sphinx")
        with open(os.path.join(temp, "out_cmdref.tex"), "w", encoding="utf8") as f:
            f.write(html)

        t1 = "this code shoud appear"
        if t1 not in html:
            raise Exception(html)

        t1 = "\\PYGZhy{}"
        if t1 not in html:
            raise Exception(html)

        t1 = '\\PYG{n}{status}'
        if t1 not in html:
            raise Exception(html)

        t1 = 'indexcmdref-freg0'
        if t1 not in html:
            raise Exception(html)

    def test_latex_builder_sphinx_table(self):
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
                        writer="elatex", keep_warnings=True,
                        directives=tives, layout="sphinx")

        temp = get_temp_folder(__file__, "temp_latex_builder_sphinx")
        with open(os.path.join(temp, "out_cmdref.tex"), "w", encoding="utf8") as f:
            f.write(html)

        t1 = "+--------+----------+"
        if t1 in html:
            raise Exception(html)

        t1 = "a&b1"
        t1b = "a&\\sphinxAtStartParb1"  # sphinx 3.5
        if t1 not in html.replace("\n", "") and t1b not in html.replace("\n", ""):
            raise Exception(html)

        t1 = "\\begin{tabulary}{\\linewidth}[t]{|T|T|}"
        if t1 not in html.replace("\n", ""):
            raise Exception(html)

    def test_latex_only(self):
        from docutils import nodes as skip_

        content = """
                    test a directive
                    ================

                    .. only:: html

                        only for html

                    .. only:: md

                        only for md

                    """.replace("                    ", "")
        content = content.replace('u"', '"')

        tives = [("cmdref", CmdRef, cmdref_node,
                  visit_cmdref_node, depart_cmdref_node)]

        text = rst2html(content,  # fLOG=fLOG,
                        writer="elatex", keep_warnings=True,
                        directives=tives, extlinks={'issue': ('http://%s', '_issue_%s')})

        temp = get_temp_folder(__file__, "temp_only")
        with open(os.path.join(temp, "out_cmdref.tex"), "w", encoding="utf8") as f:
            f.write(text)

        t1 = "only for md"
        if t1 not in text:
            raise Exception(text)
        t1 = "only for html"
        if t1 in text:
            raise Exception(text)

        text = rst2html(content,  # fLOG=fLOG,
                        writer="html", keep_warnings=True,
                        directives=tives, extlinks={'issue': ('http://%s', '_issue_%s')})

        temp = get_temp_folder(__file__, "temp_only")
        with open(os.path.join(temp, "out_cmdref.tex"), "w", encoding="utf8") as f:
            f.write(text)

        t1 = "only for md"
        if t1 in text:
            raise Exception(text)
        t1 = "only for html"
        if t1 not in text:
            raise Exception(text)

    def test_latex_reference(self):
        from docutils import nodes as skip_

        content = """
                    test a directive
                    ================

                    :py:class:`pyquickhelper.sphinxext.sphinx_latex_builder.EnhancedLaTeXBuilder`

                    :py:class:`Renamed <pyquickhelper.sphinxext.sphinx_latex_builder.EnhancedLaTeXBuilder>`
                    """.replace("                    ", "")
        content = content.replace('u"', '"')

        tives = [("cmdref", CmdRef, cmdref_node,
                  visit_cmdref_node, depart_cmdref_node)]

        text = rst2html(content,  # fLOG=fLOG,
                        writer="elatex", keep_warnings=True, layout='sphinx',
                        directives=tives, extlinks={'issue': ('http://%s', '_issue_%s')})

        temp = get_temp_folder(__file__, "temp_only")
        with open(os.path.join(temp, "out_cmdref.tex"), "w", encoding="utf8") as f:
            f.write(text)

        t1 = "pyquickhelper.sphinxext.sphinx\\_latex\\_builder.EnhancedLaTeXBuilder"
        if t1 not in text:
            raise Exception(text)
        t1 = "Renamed"
        if t1 not in text:
            raise Exception(text)
        t1 = "sphinxupquote{Renamed}"
        if t1 not in text:
            raise Exception(text)

    def test_latex_reference2(self):
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
        content = content.replace('u"', '"')

        text = rst2html(content,  # fLOG=fLOG,
                        writer="elatex", keep_warnings=False, layout='sphinx',
                        extlinks={'issue': ('http://%s', '_issue_%s')})

        self.assertIn("\\sphinxstyleemphasis{italic}", text)
        self.assertIn("bul1", text)
        self.assertIn("\\item", text)
        self.assertIn("sphinxVerbatim", text)
        self.assertNotIn("hhhh", text)
        self.assertNotIn("jjjj", text)
        self.assertNotIn("SYSTEM", text)
        temp = get_temp_folder(__file__, "temp_only")
        with open(os.path.join(temp, "out_cmdref.tex"), "w", encoding="utf8") as f:
            f.write(text)

    def test_latex_title(self):
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
        content = content.replace('u"', '"')

        text = rst2html(content,  # fLOG=fLOG,
                        writer="elatex", keep_warnings=False, layout='sphinx',
                        extlinks={'issue': ('http://%s', '_issue_%s')})

        self.assertIn("\\chapter{title2}", text)
        self.assertIn("\\section{title3}", text)
        temp = get_temp_folder(__file__, "temp_latex_title")
        with open(os.path.join(temp, "out_md_title.tex"), "w", encoding="utf8") as f:
            f.write(text)

    def test_latex_image(self):

        temp = get_temp_folder(__file__, "temp_latex_image")
        root = os.path.abspath(os.path.dirname(__file__))
        img1 = os.path.join(root, "data", "image", "im.png")
        img2 = os.path.join(root, "data", "thumbnail", "im.png")
        img1 = img1[2:]
        img2 = img2[2:]
        content = """
                    .. image:: {0}
                        :width: 59
                        :alt: alternative1

                    * .. image:: {1}
                        :width: 59
                        :alt: alternative2
                    """.replace("                    ", "").format(img1, img2).replace("\\", "/")
        content = content.replace('u"', '"')

        text = rst2html(content,  # fLOG=fLOG,
                        writer="elatex", keep_warnings=False, layout='sphinx',
                        extlinks={'issue': ('http://%s', '_issue_%s')},
                        md_image_dest=temp)

        text = text.replace("\r", "")
        self.assertIn('sphinxincludegraphics', text)
        self.assertIn('=59', text)
        self.assertIn("png", text)
        with open(os.path.join(temp, "elatex_image.tex"), "w", encoding="utf8") as f:
            f.write(text)

    def test_latex_image_overwrite(self):

        temp = get_temp_folder(__file__, "temp_latex_image_overwrite")
        root = os.path.abspath(os.path.dirname(__file__))
        img1 = os.path.join(root, "data", "image", "im.png")
        img2 = os.path.join(root, "data", "thumbnail", "im.png")
        img1 = img1[2:]
        img2 = img2[2:]
        content = """
                    .. image:: {0}
                        :width: 59
                        :alt: alternative1

                    * .. image:: {1}
                        :width: 59
                        :alt: alternative2
                    """.replace("                    ", "").format(img1, img2).replace("\\", "/")
        content = content.replace('u"', '"')

        text = rst2html(content,  # fLOG=fLOG,
                        writer="elatex", keep_warnings=False, layout='sphinx',
                        extlinks={'issue': ('http://%s', '_issue_%s')},
                        md_image_dest=temp, override_image_directive=True)

        text = text.replace("\r", "")
        self.assertIn('sphinxincludegraphics', text)
        self.assertIn('=59', text)
        self.assertIn("png", text)
        with open(os.path.join(temp, "elatex_image.tex"), "w", encoding="utf8") as f:
            f.write(text)


if __name__ == "__main__":
    unittest.main()
