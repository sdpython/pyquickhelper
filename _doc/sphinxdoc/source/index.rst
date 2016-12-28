
pyquickhelper documentation
===========================

.. image:: https://travis-ci.org/sdpython/pyquickhelper.svg?branch=master
    :target: https://travis-ci.org/sdpython/pyquickhelper
    :alt: Build Status Linux

.. image:: https://ci.appveyor.com/api/projects/status/54vl69ssd8ud4l64?svg=true
    :target: https://ci.appveyor.com/project/sdpython/pyquickhelper
    :alt: Build Status Windows

.. image:: https://badge.fury.io/py/pyquickhelper.svg
    :target: http://badge.fury.io/py/pyquickhelper

.. image:: https://img.shields.io/badge/license-MIT-blue.svg
    :alt: MIT License
    :target: http://opensource.org/licenses/MIT

.. image:: https://landscape.io/github/sdpython/pyquickhelper/master/landscape.svg?style=flat
   :target: https://landscape.io/github/sdpython/pyquickhelper/master
   :alt: Code Health

.. image:: https://requires.io/github/sdpython/pyquickhelper/requirements.svg?branch=master
     :target: https://requires.io/github/sdpython/pyquickhelper/requirements/?branch=master
     :alt: Requirements Status

.. image:: https://codecov.io/github/sdpython/pyquickhelper/coverage.svg?branch=master
    :target: https://codecov.io/github/sdpython/pyquickhelper?branch=master

.. image:: http://img.shields.io/github/issues/sdpython/pyquickhelper.png
    :alt: GitHub Issues
    :target: https://github.com/sdpython/pyquickhelper/issues

.. image:: https://badge.waffle.io/sdpython/pyquickhelper.png?label=ready&title=Ready
    :alt: Waffle
    :target: https://waffle.io/sdpython/pyquickhelper

**Links:** `pypi <https://pypi.python.org/pypi/pyquickhelper/>`_,
`github <https://github.com/sdpython/pyquickhelper>`_,
`documentation <http://www.xavierdupre.fr/app/pyquickhelper/helpsphinx/index.html>`_,
`wheel <http://www.xavierdupre.fr/site2013/index_code.html#pyquickhelper>`_,
`travis <https://travis-ci.org/sdpython/pyquickhelper>`_,
:ref:`l-README`,
:ref:`blog <ap-main-0>`,
:ref:`l-issues-todolist`,
:ref:`l-completed-todolist`

What is it?
-----------

This module contains the automation process used by all the modules I write
including my teachings. Magic commands, `Jenkins <https://jenkins-ci.org/>`_ jobs,
notebook conversion into slides, scripts to build setups, documentation, unit tests.

Quick start
-----------

.. toctree::
    :maxdepth: 1

    i_ex
    i_nb
    i_faq

Galleries
---------

.. toctree::
    :maxdepth: 2

    gyexamples/index
    all_notebooks

Functionalities
---------------

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
  (see :func:`run_doc_server <pyquickhelper.serverdoc.documentation_server.run_doc_server>`)
* function :func:`rst2html <pyquickhelper.helpgen.convert_doc_helper.rst2html>` to convert RST into HTML
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

Installation
------------

The module works for Python 3.4. Most of the functionalities were recently ported to Python 2.7 as well (not the same source code).
Both versions are available on `pipy <https://pypi.python.org/pypi/pyquickhelper>`_.

::

    pip install pyquickhelper

And to avoid installing the dependencies::

    pip install pyquickhelper --no-deps

Others options are described at: :ref:`l-moreinstall`.

Navigation
----------

.. toctree::
    :maxdepth: 1

    license
    contribute
    glossary
    issues_todoextlist
    indexmenu

+----------------------+---------------------+---------------------+--------------------+------------------------+------------------------------------------------+
| :ref:`l-modules`     |  :ref:`l-functions` | :ref:`l-classes`    | :ref:`l-methods`   | :ref:`l-staticmethods` | :ref:`l-properties`                            |
+----------------------+---------------------+---------------------+--------------------+------------------------+------------------------------------------------+
| :ref:`modindex`      |  :ref:`l-EX2`       | :ref:`search`       | :ref:`l-license`   | :ref:`l-changes`       | :ref:`l-README`                                |
+----------------------+---------------------+---------------------+--------------------+------------------------+------------------------------------------------+
| :ref:`genindex`      |  :ref:`l-FAQ2`      | :ref:`l-notebooks`  | :ref:`l-NB2`       | :ref:`l-statcode`      | `Unit Test Coverage <coverage/index.html>`_    |
+----------------------+---------------------+---------------------+--------------------+------------------------+------------------------------------------------+
