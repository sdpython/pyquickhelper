

.. _l-README:

README / Changes
================

.. image:: https://travis-ci.org/sdpython/pyquickhelper.svg?branch=master
    :target: https://travis-ci.org/sdpython/pyquickhelper
    :alt: Build status
    

**Links:**
    * `pypi/pyquickhelper <https://pypi.python.org/pypi/pyquickhelper/>`_
    * `GitHub/pyquickhelper <https://github.com/sdpython/pyquickhelper>`_
    * `documentation <http://www.xavierdupre.fr/app/pyquickhelper/helpsphinx/index.html>`_
    * `Windows Setup <http://www.xavierdupre.fr/site2013/index_code.html#pyquickhelper>`_
    * `Travis/pyquickhelper <https://travis-ci.org/sdpython/pyquickhelper>`_

Functionalities
---------------

    * simple forms in notebooks
    * help generation including notebook conversion
    * folder synchronization
    * logging
    * help running unit tests
    * simple server to server sphinx documentation
    * file compression, zip, gzip, 7z
    * helpers for ipython notebooks

Design
------

This project contains the following folders:
   * a source folder: ``src``
   * a unit test folder: ``_unittests``, go to this folder and run ``run_unittests.py``
   * a _doc folder: ``_doc``, it will contain the documentation
   * a file ``setup.py`` to build and to install the module, if the source were retrieve from GitHub,
     the script can also be called with the following extra options (``python setup.py <option>``):
     
        - clean_space: remove extra spaces in the code
        - clean_pyd: remove files *.pyd
        - build_sphinx: builds the documentation
        - unittests: run the unit tests, compute the code coverage
        
   * a script ``build_setup_help_on_windows.bat`` which run the unit tests, builds the setups and generate the documentaton on Windows
   * a script ``build_setup_help_on_linux.sh`` which does almost the same on Linux
   * a script ``publish_on_pipy.bat``

Versions / Changes
------------------

* **1.0 - 2015/??/??**
    * **new:** function to run a notebook end to end :func:`run_notebook <pyquickhelper.ipythonhelper.notebook_helper.run_notebook>`
    * **change:** function :func:`str_to_datetime <pyquickhelper.loghelper.convert_helper.str_to_datetime>` implicitely handles more formats
    * **change:** rename ``FileTreeStatus`` into :class:`FilesStatus <pyquickhelper.filehelper.files_status.FilesStatus>`
    * **new:** class :class:`FolderTransferFTP <pyquickhelper.filehelper.ftp_transfer_files.FolderTransferFTP>`
    * **new:** function :func:`remove_diacritics <pyquickhelper.texthelper.diacritic_helper.remove_diacritics>`
    * **new:** function :func:`docstring2html <pyquickhelper.helpgen.convert_doc_helper.docstring2html>` which converts RST documentation into HTML module IPython can display
    * **add:** run unit tests on `Travis-CI <https://travis-ci.org/sdpython/pyquickhelper>`_
    * **change:** renamed ``df_to_html`` into :func:`df2html <pyquickhelper.pandashelper.tblformat.df2html>`, ``df_to_rst`` into :func:`df2rst <pyquickhelper.pandashelper.tblformat.df2rst>`
    * **new:** function :func:`py3to2_convert_tree <pyquickhelper.pycode.py3to2.py3to2_convert_tree>` to convert files from python 3 to 2
* **0.9 - 2015/01/25**
    * **add:** function to remove extra spaces in a file :func:`remove_extra_spaces <pyquickhelper.pycode.code_helper.remove_extra_spaces>`
    * **add:** function :func:`create_visual_diff_through_html_files <pyquickhelper.filehelper.visual_sync.create_visual_diff_through_html_files>`
    * **fix:** the setup does not need the file ``README.rst`` anymore
    * **add:** function :func:`open_html_form <pyquickhelper.ipythonhelper.html_forms.open_html_form>`
    * **fix:** fix a bad link to `MathJax <http://www.mathjax.org/>`_ when converting notebook to HTML format
    * **add:** add parameter timeout in function :func:`run_cmd <pyquickhelper.loghelper.flog.run_cmd>`
    * **fix:** :func:`run_cmd <pyquickhelper.loghelper.flog.run_cmd>` now accepts something on the standard input
    * **new:** class :class:`MagicCommandParser <pyquickhelper.ipythonhelper.magic_parser.MagicCommandParser>`
    * **fix:** better behavior while running the unit test, add an option to compute the coverage
    * **change:** catch warnings when running the unit tests
    * **change:** expose the function :func:`process_notebooks <pyquickhelper.helpgen.sphinx_main.process_notebooks>` to convert a notebook into html, pdf, rst, docx formats
    * **add:** add simple statistics while generation the documentation
    * **add:** add function :func:`clone <pyquickhelper.loghelper.repositories.pygit_helper.clone>` and :func:`rebase <pyquickhelper.loghelper.repositories.pygit_helper.rebase>` to clone or pull rebase a git repository
    * **new:** function :func:`set_sphinx_variables <pyquickhelper.helpgen.default_conf.set_sphinx_variables>` to avoid copying the same configuration file over multiple projects
    * **del:** remove folder *sync*, move everything to *filehelper*
    * **new:** function :func:`zip7_files <pyquickhelper.filehelper.compression_helper.zip7_files>`
    * **new:** class :class:`MagicClassWithHelpers <pyquickhelper.ipythonhelper.magic_class.MagicClassWithHelpers>`
* **0.8 - 2014/11/03**
    * **add:** Python version is now checked, ImportError is raised if it used on Python 2
    * **new:** function :func:`run_doc_server <pyquickhelper.serverdoc.documentation_server.run_doc_server>` creates a local server to display documentation
    * **change:** password, password1, password2, password3 are hidden by stars when open a param window
