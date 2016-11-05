"""
@brief      test log(time=4s)
@author     Xavier Dupre
"""

import sys
import os
import unittest
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
from src.pyquickhelper.sphinxext import BlogPostList, BlogPostDirective

if sys.version_info[0] == 2:
    FileNotFoundError = Exception


class TestBlogList(unittest.TestCase):

    def test_blog_list(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        if sys.version_info[0] == 2:
            # not the same relative path for blogs, we skip
            return

        directives.register_directive("blogpost", BlogPostDirective)

        path = os.path.abspath(os.path.split(__file__)[0])
        blog = os.path.normpath(os.path.join(
            path, "..", "..", "_doc", "sphinxdoc", "source", "blog"))
        if not os.path.exists(blog):
            raise FileNotFoundError(blog)
        BlogPostList(blog, fLOG=fLOG)


if __name__ == "__main__":
    unittest.main()
