"""
@file
@brief Shortcuts to ipythonhelper
"""

from .cython_helper import ipython_cython_extension
from .helper_in_notebook import store_notebook_path, set_notebook_name_theNotebook, add_notebook_menu, load_extension
from .html_forms import open_html_form
from .interact import StaticInteract
from .jupyter_cmd import jupyter_cmd
from .kindofcompletion import AutoCompletion, AutoCompletionFile
from .magic_class import MagicClassWithHelpers
from .magic_parser import MagicCommandParser
from .notebook_exception import NotebookException, InNotebookException, JupyterException
from .notebook_helper import upgrade_notebook, read_nb, find_notebook_kernel, get_notebook_kernel
from .notebook_helper import install_jupyter_kernel, install_python_kernel_for_unittest, remove_kernel
from .notebook_helper import install_notebook_extension, get_installed_notebook_extension, get_jupyter_datadir
from .notebook_helper import remove_execution_number
from .notebook_runner import NotebookError, NotebookRunner
from .run_notebook import execute_notebook_list, run_notebook
from .widgets import RangeWidget, DropDownWidget, RadioWidget
