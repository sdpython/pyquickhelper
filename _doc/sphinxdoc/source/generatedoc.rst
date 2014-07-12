Generate this documentation
===========================


.. generatedoc:

The documentation can be written using `RST <http://sphinx-doc.org/rest.html>`_ format
or `javadoc <http://en.wikipedia.org/wiki/Javadoc>`_ format.
The program ``make_help.py`` without any required change except mention in the introduction. 
Just run it. It will go through the following steps:

    * it will copy all files found in ``src`` in folder ``_doc/sphinxdoc/source/[project_name]``
    * it will replace all relative import by absolute import (by adding proper 
    * it will generates a file .rst for each python file in ``_doc/sphinxdoc/source/[project_name]``
    * it will run the generation of the documentation using Sphinx.
    * notebooks can be placed in ``_doc/notebooks``, they will be added to the documentation
    
The results are stored in folder ``_doc/sphinxdoc/build``. On Windows,
the batch file ``build_setup_help_on_windows.bat`` copies all files
into ``dist/html``.


Configuration:
    * :ref:`l-confpy`
    
Design
++++++

The module is organized as follows:

    * ``pyquickhelper/src/pyquickhelper``: contains the sources of the modules
    * ``pyquickhelper/_unittests/``: contains the unit tests, they can run with program ``run_unittests.py``
    * ``pyquickhelper/_unittests/_doc/notebooks``: contains the notebooks included in the documentation
    * ``pyquickhelper/_unittests/_doc/sphinxdoc/source``: contains the sphinx documentation

When the documentation is being generated (by script ``pyquickhelper/make_help.py``, 
the sources are copied into ``pyquickhelper/_unittests/_doc/sphinxdoc/source/pyquickhelper``.
The documentation in `javadoc <http://en.wikipedia.org/wiki/Javadoc>`_ format is replaced by the RST syntax. Various
files are automatically generated (indexes, examples, FAQ).
Then `sphinx <http://sphinx-doc.org/>`_ is run.

After the documentation is generated, everything is copied into folder
``pyquickhelper/dist``.
    
 
Extensions to install
+++++++++++++++++++++

* `Sphinx <http://sphinx-doc.org/>`_
* `fancybox <http://spinus.github.io/sphinxcontrib-fancybox/>`_
