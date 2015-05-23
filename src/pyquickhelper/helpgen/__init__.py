"""
@file
@brief Subpart related to the documentation generation.
"""


def get_help_usage():
    """
    returns the usage ``python setup.py build_sphinx``
    """
    return """
        This command will build the documentation form the source.
        It will not work from the installed package.
        This is a custom build, the regular options with build_sphinx will not work.
        The output will be copied in folder dist.

        Usage:

            python setup.py build_sphinx
        """.replace("        ", "")


from .sphinx_main import generate_help_sphinx, process_notebooks
from .utils_sphinx_config import NbImage
from .convert_doc_helper import docstring2html
from .blog_post import BlogPost
from .blog_post_list import BlogPostList
from .sphinx_blog_extension import BlogPostDirective, BlogPostDirectiveAgg
from .sphinx_helper import sphinx_add_scripts
from .process_notebook_api import nb2slides, nb2html
