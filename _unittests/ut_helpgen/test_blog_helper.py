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
from src.pyquickhelper import get_temp_folder
from src.pyquickhelper.helpgen.utils_sphinx_doc import private_migrating_doxygen_doc
from src.pyquickhelper.helpgen import BlogPost, BlogPostList, BlogPostDirective


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
        assert p.title == "An example of a blog post included in the documentation"
        assert p.date == "2015-04-04"
        assert p.keywords == "example, blogpost, documentation"
        assert p.categories == "documentation, example"
        assert isinstance(p.Fields, dict)
        assert p.Tag == "post-2015-04-04-anexampleofablogpostincludedinthedocumentation"

    def test_post_list(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        directives.register_directive("blogpost", BlogPostDirective)

        path = os.path.abspath(os.path.split(__file__)[0])
        fold = os.path.join(path, "data")
        out = get_temp_folder(__file__, "temp_post_list")
        p = BlogPostList(fold)
        cats = p.get_categories()
        fLOG(cats)
        months = p.get_months()
        fLOG(months)
        assert cats == ['documentation', 'example']
        assert months == ['2015-04']

        res = p.write_aggregated(out)
        assert len(res) >= 4
        for r in res:
            assert os.path.exists(r)


if __name__ == "__main__":
    unittest.main()
