
pycode: helpers for unit tests and setup
========================================

.. contents::
    :local:

packages
++++++++

.. autofunction:: pyquickhelper.pycode.pip_helper.get_package_info

.. autofunction:: pyquickhelper.pycode.pip_helper.get_packages_list

python2
+++++++

.. autofunction:: pyquickhelper.pycode.py3to2.py3to2_convert

.. autofunction:: pyquickhelper.pycode.py3to2.py3to2_convert_tree

setup
+++++

.. autofunction:: pyquickhelper.pycode.setup_helper.available_commands_list

.. autofunction:: pyquickhelper.pycode.setup_helper.process_standard_options_for_setup

traceback
+++++++++

.. autofunction:: pyquickhelper.pycode.trace_execution.get_call_stack

unit tests
++++++++++

.. autofunction:: pyquickhelper.pycode.utils_tests_helper.add_missing_development_version

.. autofunction:: pyquickhelper.pycode.utils_tests_helper.check_pep8

.. autofunction:: pyquickhelper.pycode.tkinter_helper.fix_tkinter_issues_virtualenv

.. autofunction:: pyquickhelper.pycode.utils_tests_helper.get_temp_folder

.. autofunction:: pyquickhelper.pycode.ci_helper.is_travis_or_appveyor

virtual environments
++++++++++++++++++++

.. autofunction:: pyquickhelper.pycode.venv_helper.check_readme_syntax

.. autofunction:: pyquickhelper.pycode.venv_helper.compare_module_version

.. autofunction:: pyquickhelper.pycode.venv_helper.create_virtual_env

.. autofunction:: pyquickhelper.pycode.venv_helper.is_virtual_environment

.. autofunction:: pyquickhelper.pycode.venv_helper.run_base_script

.. autofunction:: pyquickhelper.pycode.venv_helper.run_venv_script
