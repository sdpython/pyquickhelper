
jupyter: run notebooks, completion in a notebook, notebook kernels, magic commands
==================================================================================

.. contents::
    :local:

completion
++++++++++

.. autoclass:: pyquickhelper.ipythonhelper.kindofcompletion.AutoCompletion
    :members:

.. autoclass:: pyquickhelper.ipythonhelper.kindofcompletion.AutoCompletionFile
    :members:

controls
++++++++

.. autofunction:: pyquickhelper.ipythonhelper.html_forms.open_html_form

.. autoclass:: pyquickhelper.ipythonhelper.interact.StaticInteract
    :members:

.. autoclass:: pyquickhelper.ipythonhelper.widgets.DropDownWidget
    :members:

.. autoclass:: pyquickhelper.ipythonhelper.widgets.RangeWidget
    :members:

.. autoclass:: pyquickhelper.ipythonhelper.widgets.RadioWidget
    :members:

.. autoclass:: pyquickhelper.ipythonhelper.widgets.RangeWidget
    :members:

extensions
++++++++++

.. autofunction:: pyquickhelper.ipythonhelper.cython_helper.ipython_cython_extension

.. autofunction:: pyquickhelper.ipythonhelper.helper_in_notebook.load_extension

kernels
+++++++

.. autofunction:: pyquickhelper.ipythonhelper.notebook_helper.find_notebook_kernel

.. autofunction:: pyquickhelper.ipythonhelper.notebook_helper.get_installed_notebook_extension

.. autofunction:: pyquickhelper.ipythonhelper.notebook_helper.get_jupyter_datadir

.. autofunction:: pyquickhelper.ipythonhelper.notebook_helper.get_notebook_kernel

.. autofunction:: pyquickhelper.ipythonhelper.notebook_helper.install_jupyter_kernel

.. autofunction:: pyquickhelper.ipythonhelper.notebook_helper.install_notebook_extension

.. autofunction:: pyquickhelper.ipythonhelper.notebook_helper.install_python_kernel_for_unittest

.. autofunction:: pyquickhelper.ipythonhelper.notebook_helper.remove_kernel

.. autofunction:: pyquickhelper.ipythonhelper.notebook_helper.upgrade_notebook

magic commands
++++++++++++++

.. autoclass:: pyquickhelper.ipythonhelper.magic_class.MagicClassWithHelpers
    :members:

.. autoclass:: pyquickhelper.ipythonhelper.magic_parser.MagicCommandParser
    :members:

notebook
++++++++

.. autofunction:: pyquickhelper.helpgen.process_notebook_api.nb2html

.. autofunction:: pyquickhelper.helpgen.process_notebook_api.nb2present

.. autofunction:: pyquickhelper.helpgen.process_notebook_api.nb2slides

.. autofunction:: pyquickhelper.ipythonhelper.run_notebook.execute_notebook_list

.. autofunction:: pyquickhelper.helpgen.utils_sphinx_config.NbImage

.. autofunction:: pyquickhelper.helpgen.sphinx_main.process_notebooks

.. autofunction:: pyquickhelper.ipythonhelper.notebook_helper.read_nb

.. autofunction:: pyquickhelper.ipythonhelper.notebook_helper.remove_execution_number

.. autofunction:: pyquickhelper.ipythonhelper.run_notebook.run_notebook
