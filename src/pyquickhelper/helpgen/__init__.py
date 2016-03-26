"""
@file
@brief Subpart related to the documentation generation.
"""
from .blog_post import BlogPost
from .blog_post_list import BlogPostList
from .convert_doc_helper import rst2html, docstring2html, HTMLWriterWithCustomDirectives
from .default_conf import set_sphinx_variables, custom_setup
from .helpgen_exceptions import HelpGenException, ImportErrorHelpGen, HelpGenConvertError
from .process_notebook_api import nb2slides, nb2html
from .sphinx_runpython_extension import RunPythonDirective, runpython_node
from .sphinx_sharenet_extension import ShareNetDirective, sharenet_node, sharenet_role
from .sphinx_bigger_extension import bigger_node, bigger_role
from .sphinx_blog_extension import BlogPostDirective, BlogPostDirectiveAgg
from .sphinx_custom_app import CustomSphinxApp
from .sphinx_helper import sphinx_add_scripts
from .sphinx_main import generate_help_sphinx, process_notebooks
from .utils_sphinx_config import NbImage
from .utils_pywin32 import import_pywin32


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
