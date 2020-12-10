"""
@file
@brief shortcuts fror pycode
"""
from .ci_helper import is_travis_or_appveyor
from .clean_helper import clean_files
from .code_helper import remove_extra_spaces_and_pep8, remove_extra_spaces_folder
from .coverage_helper import publish_coverage_on_codecov, coverage_combine
from .pip_helper import get_packages_list, get_package_info
from .readme_helper import clean_readme
from .setup_helper import (
    process_standard_options_for_setup, write_version_for_setup,
    process_standard_options_for_setup_help)
from .setup_helper import available_commands_list
from .tkinter_helper import fix_tkinter_issues_virtualenv
from .trace_execution import get_call_stack
from .unittestclass import (
    ExtTestCase, skipif_appveyor, skipif_travis, skipif_circleci,
    skipif_linux, skipif_vless, skipif_azure_macosx,
    skipif_azure, skipif_azure_linux, unittest_require_at_least,
    ignore_warnings, testlog, assert_almost_equal_detailed)
from .pytest_helper import run_test_function, TestExecutionError
from .utils_tests import main_wrapper_tests
from .utils_tests_helper import get_temp_folder, check_pep8, add_missing_development_version
from .venv_helper import (
    create_virtual_env, run_venv_script, run_base_script,
    NotImplementedErrorFromVirtualEnvironment, is_virtual_environment,
    check_readme_syntax)
