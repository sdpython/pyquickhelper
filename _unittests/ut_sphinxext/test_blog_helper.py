"""
@brief      test log(time=4s)
@author     Xavier Dupre
"""

import sys
import os
import unittest
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
from src.pyquickhelper.pycode import get_temp_folder
from src.pyquickhelper.sphinxext import BlogPost, BlogPostList, BlogPostDirective
from src.pyquickhelper.helpgen import rst2html
from src.pyquickhelper.sphinxext import RunPythonDirective


if sys.version_info[0] == 2:
    from codecs import open


class TestBlogHelper(unittest.TestCase):

    def test_post_parse(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        directives.register_directive("blogpost", BlogPostDirective)

        path = os.path.abspath(os.path.split(__file__)[0])
        file = os.path.join(path, "data", "2015-04-04_first_blogpost.rst")
        p = BlogPost(file)
        fLOG(p.title)
        self.assertEqual(
            p.title, "An example of a blog post included in the documentation")
        self.assertEqual(p.date, "2015-04-04")
        self.assertEqual(p.keywords, "example, blogpost, documentation")
        self.assertEqual(p.categories, "documentation, example")
        self.assertTrue(isinstance(p.Fields, dict))
        self.assertEqual(
            p.Tag, "post-2015-04-04-anexampleofablogpostincludedinthedocumentation")

    def test_post_list(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        # the test will fail if you add a file in data/blog others
        # with rst files which is not a blog post

        directives.register_directive("blogpost", BlogPostDirective)

        path = os.path.abspath(os.path.split(__file__)[0])
        fold = os.path.join(path, "data", "blog")
        out = get_temp_folder(__file__, "temp_post_list")
        p = BlogPostList(fold)
        cats = p.get_categories()
        fLOG(cats)
        months = p.get_months()
        fLOG(months)
        self.assertEqual(cats, ['documentation', 'example'])
        self.assertEqual(months, ['2015-04'])

        res = p.write_aggregated(out)
        self.assertTrue(len(res) >= 4)
        print(res)
        for r in res:
            if not os.path.exists(r):
                raise FileNotFoundError(r)

    def test_directive_with_rst2html(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        path = os.path.abspath(os.path.split(__file__)[0])
        file = os.path.join(path, "data", "2015-04-04_first_blogpost.rst")
        with open(file, "r", encoding="utf8") as f:
            content = f.read()

        html = rst2html(content,  # fLOG=fLOG,
                        writer="custom", keep_warnings=True)

        t1 = "<p>Text before the blog post.</p>"
        t2 = "<p>Text after the blog post.</p>"
        self.assertTrue(t1 in html)
        self.assertTrue(t2 in html)
        if "it was difficult" not in html:
            p1 = html.find(t1) + len(t1)
            p2 = html.find(t2)
            fLOG("--------------ERRORS\n", html[p1:p2], "------------")

    def test_docutils(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        # from https://gist.github.com/mastbaum/2655700
        import docutils.core
        from docutils.nodes import TextElement, Inline
        from docutils.parsers.rst import Directive, directives
        from docutils.writers.html4css1 import Writer, HTMLTranslator

        class foo(Inline, TextElement):
            pass

        class Foo(Directive):
            required_arguments = 1
            optional_arguments = 0
            has_content = True

            def run(self):
                thenode = foo(text=self.arguments[0])
                return [thenode]

        class MyHTMLTranslator(HTMLTranslator):

            def __init__(self, document):
                HTMLTranslator.__init__(self, document)

            def visit_foo(self, node):
                self.body.append(self.starttag(
                    node, 'span', '', style='background:red'))
                self.body.append("<!--foo-->")

            def depart_foo(self, node):
                self.body.append('<!--foo--></span>')

        directives.register_directive('foo', Foo)
        html_writer = Writer()
        html_writer.translator_class = MyHTMLTranslator

        rest_text = '''
        this is a test
        ==============
        it is only a test

        .. foo:: whee

        '''.replace("        ", "")

        bhtml = docutils.core.publish_string(
            source=rest_text, writer=html_writer)
        typstr = str  # unicode#
        html = typstr(bhtml, encoding="utf8")
        if "<!--foo-->" not in html:
            raise Exception(html)

    def test_newdirective_with_rst2html(self):
        """
        this test also test the extension runpython
        """
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        if sys.version_info[0] == 2:
            warnings.warn(
                "test_newdirective_with_rst2html not run on Python 2.7")
            return

        from docutils import nodes

        class runpythonthis_node(nodes.Structural, nodes.Element):
            pass

        class RunPythonThisDirective (RunPythonDirective):
            runpython_class = runpythonthis_node

        def visit_rp_node(self, node):
            self.body.append("<p><b>visit_rp_node</b></p>")

        def depart_rp_node(self, node):
            self.body.append("<p><b>depart_rp_node</b></p>")

        content = """
                    test a directive
                    ================

                    .. runpythonthis::

                        print(u"this code shoud appear" + u"___")
                    """.replace("                    ", "")
        if sys.version_info[0] >= 3:
            content = content.replace('u"', '"')

        tives = [("runpythonthis", RunPythonThisDirective, runpythonthis_node,
                  visit_rp_node, depart_rp_node)]

        html = rst2html(content,  # fLOG=fLOG,
                        writer="custom", keep_warnings=True,
                        directives=tives)

        ta = "<p><b>visit_rp_node</b></p>"
        if ta not in html:
            raise Exception(html)
        tb = "<p><b>depart_rp_node</b></p>"
        if tb not in html:
            raise Exception(html)
        t1 = "this code shoud appear___".split()
        for t in t1:
            if t not in html:
                temp = get_temp_folder(
                    __file__, "temp_newdirective_with_rst2html")
                with open(os.path.join(temp, "bug.html"), "w", encoding="utf8") as f:
                    f.write(html)
                raise Exception(html)

    def test_newdirective_with_rst2html_bug(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        from docutils import nodes

        class runpythonthis_node(nodes.Structural, nodes.Element):
            pass

        class RunPythonThisDirective (RunPythonDirective):
            runpython_class = runpythonthis_node

        def visit_node(self, node):
            self.body.append("<p><b>visit_node</b></p>")

        def depart_node(self, node):
            self.body.append("<p><b>depart_node</b></p>")

        content = """

                        description
                        -----------

                        .. deprecated:: 0.3
                            to add

                        this code shoud appear___

                    """.replace("                        ", "")

        tives = [("runpythonthis", RunPythonThisDirective, runpythonthis_node,
                  visit_node, depart_node)]

        html = rst2html(content,  # fLOG=fLOG,
                        writer="custom", keep_warnings=True,
                        directives=tives)

        t1 = "this code shoud appear___"
        self.assertTrue(t1 in html)
        ta = "Deprecated since version 0.3"
        if ta not in html:
            raise Exception(html)


if __name__ == "__main__":
    unittest.main()
