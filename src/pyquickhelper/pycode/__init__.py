"""
@file
@brief shortcuts fror pycode
"""

from .code_helper import remove_extra_spaces_and_pep8, remove_extra_spaces_folder
from .pip_helper import get_packages_list, get_package_info
from .py3to2 import py3to2_convert_tree, py3to2_convert
from .setup_helper import process_standard_options_for_setup
from .tkinter_helper import fix_tkinter_issues_virtualenv
from .trace_execution import get_call_stack
from .utils_tests import get_temp_folder, main_wrapper_tests
from .venv_helper import create_virtual_env, run_venv_script, compare_module_version
from .venv_helper import NotImplementedErrorFromVirtualEnvironment, is_virtual_environment, check_readme_syntax
from .coverage_helper import publish_coverage_on_codecov
