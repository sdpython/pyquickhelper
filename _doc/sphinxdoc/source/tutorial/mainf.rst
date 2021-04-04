
Main Functionalities
====================

*notebooks (ipython):*

* simple forms in notebooks (see :func:`open_html_form <pyquickhelper.ipythonhelper.html_forms.open_html_form>`)
* function to run a notebook offline :func:`run_notebook <pyquickhelper.ipythonhelper.run_notebook.run_notebook>`
* form interacting with Python functions in a notebook, see notebook :ref:`havingaforminanotebookrst`
* function :func:`add_notebook_menu <pyquickhelper.ipythonhelper.helper_in_notebook.add_notebook_menu>`
  automatically adds a menu in the notebook based on sections
* method to add metadata when converting a notebook into slides
  :meth:`add_tag_slide <pyquickhelper.ipythonhelper.notebook_runner.NotebookRunner.add_tag_slide>`
* method to merge notebooks :meth:`merge_notebook <pyquickhelper.ipythonhelper.notebook_runner.NotebookRunner.merge_notebook>`
* :class:`MagicCommandParser <pyquickhelper.ipythonhelper.magic_parser.MagicCommandParser>`,
  :class:`MagicClassWithHelpers <pyquickhelper.ipythonhelper.magic_class.MagicClassWithHelpers>` to help
  creating magic command for IPython notebooks,
  the parser tries to interpret values passed to the magic commands
* method :func:`nb2slides<pyquickhelper.helpgen.process_notebook_api.nb2slides>` to convert a notebook into slides

*unit tests:*

* folder synchronization (see :func:`pyquickhelper.synchronize_folder <pyquickhelper.filehelper.synchelper.synchronize_folder>`)
* logging (see :func:`fLOG <pyquickhelper.loghelper.flog.fLOG>`)
* help running unit tests (see :func:`main_wrapper_tests <pyquickhelper.pycode.utils_tests.main_wrapper_tests>`)

*automated documentation:*

* help generation including notebook conversion
  (see :func:`generate_help_sphinx <pyquickhelper.helpgen.sphinx_main.generate_help_sphinx>`)
* simple server to server sphinx documentation
  (see :func:`run_doc_server <pyquickhelper.server.documentation_server.run_doc_server>`)
* function :func:`rst2html <pyquickhelper.helpgen.sphinxm_convert_doc_helper.rst2html>`
  to convert RST into HTML
* Sphinx directive :class:`BlogPostDirective <pyquickhelper.sphinxext.sphinx_blog_extension.BlogPostDirective>`
  to add a directive ``blogpost`` into the docutmention
* Sphinx directive :class:`RunPythonDirective <pyquickhelper.sphinxext.sphinx_runpython_extension.RunPythonDirective>`
  to generate documentation from a script
* :class:`TodoExt <pyquickhelper.sphinxext.sphinx_todoext_extension.TodoExt>`
  for a richer ``todo`` directive
* :class:`ShareNetDirective <pyquickhelper.sphinxext.sphinx_sharenet_extension.ShareNetDirective>`
  to add share buttons on Facebook, Linkedin, Twitter
* :class:`MathDef <pyquickhelper.sphinxext.sphinx_mathdef_extension.MathDef>`
  defines ``mathdef`` directive, helps for documentation with mathematics

*automation:*

* function to create and delete jobs on `Jenkins <https://jenkins-ci.org/>`_,
  see :class:`JenkinsExt <pyquickhelper.jenkinshelper.jenkins_server.JenkinsExt>`
  based on build script produced by function
  :func:`process_standard_options_for_setup <pyquickhelper.pycode.setup_helper.process_standard_options_for_setup>`,
  Jenkisn jobs can be defined based on YAML script. See :ref:`l-ci-jenkins`.
* encrypted backup, see :class:`EncryptedBackup <pyquickhelper.filehelper.encrypted_backup.EncryptedBackup>`,
  the API allow to add others backup supports
* folder synchronisation, see function :func:`synchronize_folder <pyquickhelper.filehelper.synchelper.synchronize_folder>`

*encryption*

The module proposes two commands ``encrypt``, ``decrypt``, ``encrypt_file``, ``decrypt_file``::

    usage: encrypt [-h] source dest password
    usage: decrypt [-h] source dest password
    usage: encrypt_file [-h] source dest password
    usage: decrypt_file [-h] source dest password

Many functionalities about automated documentation assume the current processed
documentation follows the same design as this module.
Future enhancements are covered by :ref:`l-issues-todolist`.
