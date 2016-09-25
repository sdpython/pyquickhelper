"""
@file
@brief Shortcuts to ipythonhelper

.. todoext::
    :title: Move add_notebook_menu to jyquickhelper
    :tag: done
    :date: 2016-09-25
    :release: 1.5
    :cost: 0.3

    A couple of were functions were moved to a lighter module
    `jyquickhelper <https://pypi.python.org/pypi/jyquickhelper>`_. They will be removed in release 1.6.

    * store_notebook_path, 
    * set_notebook_name_theNotebook, 
    * add_notebook_menu
    * load_extension
"""

from .cython_helper import ipython_cython_extension
from .helper_in_notebook import store_notebook_path, set_notebook_name_theNotebook, add_notebook_menu, load_extension
from .html_forms import open_html_form
from .interact import StaticInteract
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
