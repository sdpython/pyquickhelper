"""
@file
@brief Shortcuts to ipythonhelper
"""

from .notebook_exception import NotebookException, InNotebookException, JupyterException
from .notebook_runner import NotebookError, NotebookRunner
from .notebook_helper import run_notebook, upgrade_notebook, execute_notebook_list, read_nb, find_notebook_kernel, get_notebook_kernel, install_jupyter_kernel, install_python_kernel_for_unittest, remove_kernel
from .notebook_helper import install_notebook_extension, get_installed_notebook_extension, get_jupyter_datadir
from .helper_in_notebook import store_notebook_path, set_notebook_name_theNotebook, add_notebook_menu, load_extension
from .cython_helper import ipython_cython_extension
from .magic_parser import MagicCommandParser
from .magic_class import MagicClassWithHelpers
from .kindofcompletion import AutoCompletion, AutoCompletionFile
from .html_forms import open_html_form
from .interact import StaticInteract
from .widgets import RangeWidget, DropDownWidget, RadioWidget
from .jupyter_cmd import jupyter_cmd
