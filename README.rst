.. _l-README:

README
======

.. contents::
   :depth: 3


Introduction
------------

This extension gathers three functionalities:
    * a logging function
    * a function to synchronize two folders
    * a function to generate a copy of a module, converting doxygen documentation in rst format
    
The documentation is available at 
`pyquickhelper documentation <http://www.xavierdupre.fr/app/pyquickhelper/helpsphinx/index.html>`_.
You can download the setup  `here <http://www.xavierdupre.fr/site2013/index_code.html>`_.
The module is available on `pypi/pyquickhelper <https://pypi.python.org/pypi/pyquickhelper/>`_ and
on `GitHub/pyquickhelper <https://github.com/sdpython/pyquickhelper>`_.


Design
------

This project contains various helper about logging functions, unit tests and help generation.
   * a source folder: ``src``
   * a unit test folder: ``_unittests``, go to this folder and run ``run_unittests.py``
   * a _doc folder: ``_doc``, it will contains the documentation
   * a file ``setup.py`` to build and to install the module
   * a file ``make_help.py`` to build the sphinx documentation
    
    
    
Dependencies
------------

To build the documentation, you need:
   * `Sphinx <http://sphinx-doc.org/>`_ and its dependencies.

