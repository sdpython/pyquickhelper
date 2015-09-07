"""
@brief      test log(time=4s)
@author     Xavier Dupre
"""

import sys
import os
import unittest
import sphinx
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
from src.pyquickhelper.helpgen import BlogPost, BlogPostList, BlogPostDirective, BlogPostDirectiveAgg
from src.pyquickhelper.helpgen import rst2html
from src.pyquickhelper.helpgen import RunPythonDirective, runpython_node
from src.pyquickhelper.helpgen.sphinx_runpython_extension import visit_runpython_node, depart_runpython_node

if sys.version_info[0] == 2:
    from codecs import open
    FileNotFoundError = Exception


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
        bl = BlogPostList(blog, fLOG=fLOG)

if __name__ == "__main__":
    unittest.main()
