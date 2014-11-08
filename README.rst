.. _l-README:

README
======

   
   
**Links:**
    * `pypi/pyquickhelper <https://pypi.python.org/pypi/pyquickhelper/>`_
    * `GitHub/pyquickhelper <https://github.com/sdpython/pyquickhelper>`_
    * `documentation <http://www.xavierdupre.fr/app/pyquickhelper/helpsphinx/index.html>`_
    * `Windows Setup <http://www.xavierdupre.fr/site2013/index_code.html#pyquickhelper>`_

Description
-----------

This extension gathers three functionalities:
    * a logging function: :func:`fLOG <pyquickhelper.loghelper.flog.fLOG>`
    * a function to synchronize two folders: :func:`synchronize_folder <pyquickhelper.sync.synchelper.synchronize_folder>`
    * a function to generate a copy of a module, converting doxygen documentation in rst format: :func:`generate_help_sphinx <pyquickhelper.helpgen.sphinx_main.generate_help_sphinx>` (see also :func:`prepare_file_for_sphinx_help_generation <pyquickhelper.helpgen.utils_sphinx_doc.prepare_file_for_sphinx_help_generation>`),
      it requires the module is designed as this one (`src`, `_doc` folders).
    
The module is available on `pypi/pyquickhelper <https://pypi.python.org/pypi/pyquickhelper/>`_ and
on `GitHub/pyquickhelper <https://github.com/sdpython/pyquickhelper>`_.

Functionalities
---------------

    * help generation
    * folder synchronization
    * logging
    * import a flat file into a SQLite database
    * help running unit tests
    * functions to convert a pandas DataFrame into a HTML table or a RST table

Design
------

This project contains various helper about logging functions, unit tests and help generation.
   * a source folder: ``src``
   * a unit test folder: ``_unittests``, go to this folder and run ``run_unittests.py``
   * a _doc folder: ``_doc``, it will contain the documentation
   * a file ``setup.py`` to build and to install the module
   * a file ``make_help.py`` to build the sphinx documentation
   
Versions
--------

* **0.9 - 2014/??/??**
    * **add:** function to remove extra spaces in a file :func:`remove_extra_spaces <pyquickhelper.pycode.code_helper.remove_extra_spaces>`
    * **add:** function :func:`create_visual_diff_through_html_files <pyquickhelper.sync.visual_sync.create_visual_diff_through_html_files>`
* **0.8 - 2014/11/03**
    * **add:** Python version is now checked, ImportError is raised if it used on Python 2
    * **new:** function :func:`run_doc_server <pyquickhelper.serverdoc.documentation_server.run_doc_server>` creates a local server to display documentation
    * **change:** password, password1, password2, password3 are hidden by stars when open a param window
* **0.7 - 2014/10/22**
    * **new:** function :func:`has_been_updated <pyquickhelper.sync.synchelper.has_been_updated>` to check if a copy of a file is outdated
    * **fix:** fix a bug while updating the notebook file (documentation generation)
    * **fix:** fix misspellings and some minor bugs
    * **add:** some parts can be ignored while generation the documentation by adding section ``# -- HELP BEGIN EXCLUDE --`` and ``# -- HELP END EXCLUDE --``
    * **change:** do not replace relative imports when generating the documentation
    * **change:** the documentation compiles under linux (the latex part was not tested and removed from the script ``build_setup_help_on_linux.sh``)
* **0.6 - 2014/08/24**
    * **change:** minor fixes for the documentation generation
    * **add:** add code to handle conversion of notebooks in docx format
