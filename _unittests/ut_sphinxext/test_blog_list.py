"""
@brief      test log(time=4s)
@author     Xavier Dupre
"""
import os
import unittest
from io import StringIO
from contextlib import redirect_stderr, redirect_stdout
from docutils.parsers.rst import directives
from pyquickhelper.loghelper import fLOG
from pyquickhelper.pycode import ExtTestCase, ignore_warnings
from pyquickhelper.sphinxext import BlogPostList, BlogPostDirective


class TestBlogList(ExtTestCase):

    @ignore_warnings(PendingDeprecationWarning)
    def test_blog_list(self):
        st = StringIO()
        with redirect_stdout(st):
            with redirect_stderr(st):
                directives.register_directive("blogpost", BlogPostDirective)
                path = os.path.abspath(os.path.split(__file__)[0])
                blog = os.path.normpath(os.path.join(
                    path, "..", "..", "_doc", "sphinxdoc", "source", "blog"))
                if not os.path.exists(blog):
                    raise FileNotFoundError(blog)
                BlogPostList(blog, fLOG=fLOG)


if __name__ == "__main__":
    unittest.main()
