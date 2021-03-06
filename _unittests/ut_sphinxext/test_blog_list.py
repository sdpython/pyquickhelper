"""
@brief      test log(time=4s)
@author     Xavier Dupre
"""

import sys
import os
import unittest
from docutils.parsers.rst import directives

from pyquickhelper.loghelper.flog import fLOG
from pyquickhelper.sphinxext import BlogPostList, BlogPostDirective


class TestBlogList(unittest.TestCase):

    def test_blog_list(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        directives.register_directive("blogpost", BlogPostDirective)

        path = os.path.abspath(os.path.split(__file__)[0])
        blog = os.path.normpath(os.path.join(
            path, "..", "..", "_doc", "sphinxdoc", "source", "blog"))
        if not os.path.exists(blog):
            raise FileNotFoundError(blog)
        BlogPostList(blog, fLOG=fLOG)


if __name__ == "__main__":
    unittest.main()
