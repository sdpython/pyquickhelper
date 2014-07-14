
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
    * a logging function: :func:`fLOG <loghelper.flog.fLOG>`
    * a function to synchronize two folders: :func:`synchronize_folder <sync.synchelper.synchronize_folder>`
    * a function to generate a copy of a module, converting doxygen documentation in rst format: :func:`generate_help_sphinx <helpgen.sphinx_main.generate_help_sphinx>` (see also :func:`prepare_file_for_sphinx_help_generation <helpgen.utils_sphinx_doc.prepare_file_for_sphinx_help_generation>`),
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
   * a _doc folder: ``_doc``, it will contains the documentation
   * a file ``setup.py`` to build and to install the module
   * a file ``make_help.py`` to build the sphinx documentation
   
Versions
--------

* **v0.5 - 2014/??/??**
    * **change:** few fixes while generating the documentation (notebooks, toctrees)
    * **change:** compilation of the help into PDF, latex, singlehtml
    * **change:** removes the creation of ``temp_log.txt`` by default when using function :func:`fLOG <loghelper.flog.fLOG>`
    * **fix:** the module can fix an exception thrown by ``pywin32`` about DLL missing
    * **change:** can use nbconvert from ipython 2.1 to generate the documentation
    * **new:** add function :func:`get_url_content <loghelper.url_helper.get_url_content>`
* **v0.4 - 2014/04/19**
    * **change**: add the possibility to create more than one page of examples, use tag ``@example(page___title)``
    * **change**: use method `communicate <https://docs.python.org/3.4/library/subprocess.html#subprocess.Popen.communicate>`_ in :func:`run_cmd <loghelper.flog.run_cmd>`, remove characters ``\r`` on Windows
    * **change**: more robust function :func:`run_cmd <loghelper.flog.run_cmd>`, change default values 
    * **change**: :func:`synchronize_folder <sync.synchelper.synchronize_folder>` now removes files when using a file to memorize the list of synchronized files
    * **new:** the documentation generation takes notebooks from folder ``_docs/notebooks``
