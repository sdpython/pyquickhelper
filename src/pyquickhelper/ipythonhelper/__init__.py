"""
@file
@brief Shortcuts to ipythonhelper
"""

from .notebook_runner import NotebookError, NotebookRunner
from .cython_helper import ipython_cython_extension
from .notebook_helper import run_notebook, upgrade_notebook, execute_notebook_list, set_notebook_name_theNotebook
from .magic_parser import MagicCommandParser
from .kindofcompletion import AutoCompletion
from .html_forms import open_html_form
from .interact import StaticInteract
from .widgets import RangeWidget, DropDownWidget, RadioWidget
from .helper_in_notebook import store_notebook_path
