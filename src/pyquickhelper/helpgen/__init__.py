"""
@file
@brief Subpart related to the documentation generation.
"""
from .conf_path_tools import find_graphviz_dot
from .default_conf import set_sphinx_variables, custom_setup
from .helpgen_exceptions import HelpGenException, ImportErrorHelpGen, HelpGenConvertError
from .help_usage import get_help_usage
from .pandoc_helper import latex2rst
from .process_notebook_api import nb2slides, nb2html, nb2rst
from .rst_converters import rst2html, docstring2html, rst2rst_folder
from .sphinx_helper import sphinx_add_scripts
# Disable to speed up import time.
# from .sphinx_main import generate_help_sphinx, process_notebooks
from .utils_sphinx_config import NbImage
from .utils_pywin32 import import_pywin32
