"""
@brief      test log(time=4s)
@author     Xavier Dupre
"""
import os
import unittest
from docutils.parsers.rst import directives
from pyquickhelper.pycode import (
    get_temp_folder, ignore_warnings, skipif_appveyor)
from pyquickhelper.helpgen import rst2html
from pyquickhelper.sphinxext.sphinx_blog_extension import (
    BlogPostDirective, BlogPostDirectiveAgg,
    blogpost_node, visit_blogpost_node, depart_blogpost_node,
    blogpostagg_node, visit_blogpostagg_node, depart_blogpostagg_node)


class TestBlogExtension(unittest.TestCase):

    @ignore_warnings(PendingDeprecationWarning)
    def test_post_parse_blog(self):
        directives.register_directive("blogpost", BlogPostDirective)
        directives.register_directive("blogpostagg", BlogPostDirectiveAgg)

    @ignore_warnings(PendingDeprecationWarning)
    @skipif_appveyor("Message: 'Running Sphinx v5.3.0'")
    def test_blogpost(self):

        from docutils import nodes as skip_

        content = """
                    test a directive
                    ================

                    before

                    .. blogpost::
                        :title: first blog post
                        :keywords: keyw
                        :categories: cat1
                        :date: 2018-03-24
                        :lid: id3

                        this code shoud appear___

                    after
                    """.replace("                    ", "")
        content = content.replace('u"', '"')

        tives = [("blogpost", BlogPostDirective, blogpost_node,
                  visit_blogpost_node, depart_blogpost_node)]

        text = rst2html(content,  # fLOG=fLOG,
                        layout="sphinx", writer="html", keep_warnings=True,
                        directives=tives, extlinks={'issue': ('http://%s', '_issue_')})

        temp = get_temp_folder(__file__, "temp_blog_ext")
        with open(os.path.join(temp, "out_blog.html"), "w", encoding="utf8") as f:
            f.write(text)

        self.assertIn('</span><h2 id=', text)
        self.assertIn('>2018-03-24 first', text)

        text = rst2html(content,  # fLOG=fLOG,
                        layout="sphinx", writer="rst", keep_warnings=True,
                        directives=tives, extlinks={'issue': ('http://%s', '_issue_')})

        with open(os.path.join(temp, "out_blog.rst"), "w", encoding="utf8") as f:
            f.write(text)

        self.assertIn('this code shoud appear___', text)
        self.assertIn('.. _id3:', text)
        self.assertIn('================', text)
        self.assertIn('after', text)

    @ignore_warnings(PendingDeprecationWarning)
    @skipif_appveyor("Message: 'Running Sphinx v5.3.0'")
    def test_blogpost_agg(self):

        from docutils import nodes as skip_

        content = """
                    test a directive
                    ================

                    before

                    .. blogpostagg::
                        :title: first blog post
                        :keywords: keyw
                        :categories: cat1
                        :date: 2018-03-24

                        this code shoud appear___.

                        this one not sure.

                    after
                    """.replace("                    ", "")
        content = content.replace('u"', '"')

        tives = [("blogpostagg", BlogPostDirectiveAgg, blogpostagg_node,
                  visit_blogpostagg_node, depart_blogpostagg_node)]

        text = rst2html(content,  # fLOG=fLOG,
                        layout="sphinx", writer="html", keep_warnings=True,
                        directives=tives, extlinks={'issue': ('http://%s', '_issue_')})

        temp = get_temp_folder(__file__, "temp_blogagg_ext")
        with open(os.path.join(temp, "out_blog.html"), "w", encoding="utf8") as f:
            f.write(text)

        self.assertIn('<font size="5">2018-03-24</font></p>', text)

        text = rst2html(content,  # fLOG=fLOG,
                        layout="sphinx", writer="rst", keep_warnings=True,
                        directives=tives, extlinks={'issue': ('http://%s', '_issue_')})

        with open(os.path.join(temp, "out_blog.rst"), "w", encoding="utf8") as f:
            f.write(text)

        self.assertIn('this code shoud appear___', text)
        self.assertIn('==========', text)
        self.assertIn(':bigger:`2018-03-24`', text)
        self.assertIn('after', text)


if __name__ == "__main__":
    unittest.main()
