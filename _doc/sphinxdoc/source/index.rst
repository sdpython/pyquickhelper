.. project_name documentation documentation master file, created by
   sphinx-quickstart on Fri May 10 18:35:14 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

pyquickhelper documentation
===========================


.. image:: https://travis-ci.org/sdpython/pyquickhelper.svg?branch=master
    :target: https://travis-ci.org/sdpython/pyquickhelper
    :alt: Build status
    
.. image:: https://badge.fury.io/py/pyquickhelper.svg
    :target: http://badge.fury.io/py/pyquickhelper
    
.. image:: http://img.shields.io/pypi/dm/pyquickhelper.png
    :alt: PYPI Package
    :target: https://pypi.python.org/pypi/pyquickhelper

.. image:: http://img.shields.io/github/issues/sdpython/pyquickhelper.png
    :alt: GitHub Issues
    :target: https://github.com/sdpython/pyquickhelper/issues
    
.. image:: https://img.shields.io/badge/license-MIT-blue.svg
    :alt: MIT License
    :target: http://opensource.org/licenses/MIT


**Links:** `pypi <https://pypi.python.org/pypi/pyquickhelper/>`_, 
`github <https://github.com/sdpython/pyquickhelper>`_,
`documentation <http://www.xavierdupre.fr/app/pyquickhelper/helpsphinx/index.html>`_, 
`wheel <http://www.xavierdupre.fr/site2013/index_code.html#pyquickhelper>`_,
`travis <https://travis-ci.org/sdpython/pyquickhelper>`_,
:ref:`l-README`,
:ref:`blog <ap-main-0>`


Tutorial
--------

.. toctree::
    :max_depth: 1
    
    all_example
    all_notebooks
    

Functionalities
---------------


*notebooks (ipython):*

* simple forms in notebooks (see :func:`open_html_form <pyquickhelper.ipythonhelper.html_forms.open_html_form>`)
* function to run a notebook offline :func:`run_notebook <pyquickhelper.ipythonhelper.notebook_helper.run_notebook>`
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
* Sphinx directive :class:`BlogPostDirective <pyquickhelper.helpgen.sphinx_blog_extension.BlogPostDirective>` 
  to add a directive ``blogpost`` into the docutmention
  
*automation:*

* function to create and delete jobs on `Jenkins <https://jenkins-ci.org/>`_, 
  see :class:`JenkinsExt <pyquickhelper.jenkinshelper.jenkins_server.JenkinsExt>`
  
Many functionalities about automated documentation assume the current processed
documentation follows the same design as this module.
      
Installation
------------

The module works for Python 3.4. Most of the functionalities were recently ported to Python 2.7 as well (not the same source code).
Both versions are available on `pipy <https://pypi.python.org/pypi/pyquickhelper>`_.

:: 

    pip install pyquickhelper

And to avoid installing the dependencies::

    pip install pyquickhelper --no-deps
    
    
Navigation
----------

The most simple way is with *pip*: ``pip install pyquickhelper``. 
Others options are described at: :ref:`l-moreinstall`.
    

+----------------------+---------------------+---------------------+--------------------+------------------------+------------------------------------------------+
| :ref:`l-modules`     |  :ref:`l-functions` | :ref:`l-classes`    | :ref:`l-methods`   | :ref:`l-staticmethods` | :ref:`l-properties`                            |
+----------------------+---------------------+---------------------+--------------------+------------------------+------------------------------------------------+
| :ref:`modindex`      |  :ref:`l-example`   | :ref:`search`       | :ref:`l-license`   | :ref:`l-changes`       | :ref:`l-README`                                |
+----------------------+---------------------+---------------------+--------------------+------------------------+------------------------------------------------+
| :ref:`genindex`      |  :ref:`l-FAQ`       | :ref:`l-notebooks`  |                    | :ref:`l-statcode`      | `Unit Test Coverage <coverage/index.html>`_    |
+----------------------+---------------------+---------------------+--------------------+------------------------+------------------------------------------------+


.. toctree::
    :maxdepth: 1

    indexmenu
