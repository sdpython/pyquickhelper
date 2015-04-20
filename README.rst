

.. _l-README:

README / Changes
================

.. image:: https://travis-ci.org/sdpython/pyquickhelper.svg?branch=master
    :target: https://travis-ci.org/sdpython/pyquickhelper
    :alt: Build status
    
.. image:: https://badge.fury.io/py/pyquickhelper.svg
    :target: http://badge.fury.io/py/pyquickhelper
        
.. image:: http://img.shields.io/pypi/dm/pyquickhelper.png
    :alt: PYPI Package
    :target: https://pypi.python.org/pypi/pyquickhelper

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
    * helpers for ipython notebooks (upgrade, offline run)
    * parser to quickly add a magic command in a notebook
    * Sphinx directives to integrate a blogpost in the documentation

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

* **1.0 - 2015/04/21**
    * **new:** function to run a notebook end to end :func:`run_notebook <pyquickhelper.ipythonhelper.notebook_helper.run_notebook>`
    * **change:** function :func:`str_to_datetime <pyquickhelper.loghelper.convert_helper.str_to_datetime>` implicitely handles more formats
    * **change:** rename ``FileTreeStatus`` into :class:`FilesStatus <pyquickhelper.filehelper.files_status.FilesStatus>`
    * **new:** class :class:`FolderTransferFTP <pyquickhelper.filehelper.ftp_transfer_files.FolderTransferFTP>`
    * **new:** function :func:`remove_diacritics <pyquickhelper.texthelper.diacritic_helper.remove_diacritics>`
    * **new:** function :func:`docstring2html <pyquickhelper.helpgen.convert_doc_helper.docstring2html>` which converts RST documentation into HTML module IPython can display
    * **add:** run unit tests on `Travis-CI <https://travis-ci.org/sdpython/pyquickhelper>`_
    * **change:** renamed ``df_to_html`` into :func:`df2html <pyquickhelper.pandashelper.tblformat.df2html>`, ``df_to_rst`` into :func:`df2rst <pyquickhelper.pandashelper.tblformat.df2rst>`
    * **new:** function :func:`py3to2_convert_tree <pyquickhelper.pycode.py3to2.py3to2_convert_tree>` to convert files from python 3 to 2
    * **new:** class :class:`JenkinsExt <pyquickhelper.jenkinshelper.jenkins_server.JenkinsExt>` to help creating and deleting jobs on Jenkins
    * **new:** :class:`MagicCommandParser <pyquickhelper.ipythonhelper.magic_parser.MagicCommandParser>`, 
      :class:`MagicClassWithHelpers <pyquickhelper.ipythonhelper.magic_class.MagicClassWithHelpers>` to help creating magic commands on IPython notebooks,
      the parser tries to interpret values passed to the magic commands
    * **new:** function :func:`ipython_cython_extension <pyquickhelper.ipythonhelper.cython_helper.ipython_cython_extension>` which checks if cython can work on Windows (compiler issues)
    * **new:** the automated generation of the documentation now accepts blogs to be included (in folder ``_doc/sphinxdoc/source/blog``)
    * **change:** migration to IPython 3.1 (changes when running a notebook offline, converting a notebook)
    * **new:** some functionalities of pyquickhelper are now available in python 2.7, 
      not all the functionalities using string were migrated (too much of a pain)
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
