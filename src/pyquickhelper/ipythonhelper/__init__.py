"""
@file
@brief Shortcuts to ipythonhelper
"""

from .html_forms import open_html_form
from .interact import StaticInteract
from .kindofcompletion import AutoCompletion, AutoCompletionFile
from .magic_class import MagicClassWithHelpers
from .magic_parser import MagicCommandParser
from .notebook_exception import NotebookException, InNotebookException, JupyterException
from .notebook_helper import upgrade_notebook, read_nb, read_nb_json, find_notebook_kernel, get_notebook_kernel
from .notebook_helper import install_jupyter_kernel, install_python_kernel_for_unittest, remove_kernel
from .notebook_helper import install_notebook_extension, get_installed_notebook_extension, get_jupyter_datadir
from .notebook_helper import remove_execution_number
from .notebook_runner import NotebookError, NotebookRunner
from .run_notebook import execute_notebook_list, run_notebook, execute_notebook_list_finalize_ut, retrieve_notebooks_in_folder
from .run_notebook import notebook_coverage, badge_notebook_coverage
from .run_notebook import get_additional_paths
from .unittest_notebook import test_notebook_execution_coverage
from .widgets import RangeWidget, DropDownWidget, RadioWidget
