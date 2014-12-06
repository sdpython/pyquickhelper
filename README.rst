.. _l-README:

README
======



**Links:**
    * `pypi/pyquickhelper <https://pypi.python.org/pypi/pyquickhelper/>`_
    * `GitHub/pyquickhelper <https://github.com/sdpython/pyquickhelper>`_
    * `documentation <http://www.xavierdupre.fr/app/pyquickhelper/helpsphinx/index.html>`_
    * `Windows Setup <http://www.xavierdupre.fr/site2013/index_code.html#pyquickhelper>`_

Functionalities
---------------

    * simple forms in notebooks
    * help generation including notebook conversion
    * folder synchronization
    * logging
    * help running unit tests
    * simple server to server sphinx documentation

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
    * **fix:** the setup does not need the file ``README.rst`` anymore
    * **add:** function :func:`open_html_form <pyquickhelper.ipythonhelper.html_forms.open_html_form>`
    * **fix:** fix a bad link to MathJax when converting notebook to HTML format
    * **add:** add parameter timeout in function :func:`run_cmd`
    * **fix:** :func:`run_cmd` now accepts something on the standard input
    * **new:** class :class:`MagicCommandParser <pyquickhelper.ipythonhelper.magic_parser.MagicCommandParser>`
    * **fix:** better behavior while running the unit test
* **0.8 - 2014/11/03**
    * **add:** Python version is now checked, ImportError is raised if it used on Python 2
    * **new:** function :func:`run_doc_server <pyquickhelper.serverdoc.documentation_server.run_doc_server>` creates a local server to display documentation
    * **change:** password, password1, password2, password3 are hidden by stars when open a param window
