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
 
Extensions to install
+++++++++++++++++++++

* `Sphinx <http://sphinx-doc.org/>`_
* `fancybox <http://spinus.github.io/sphinxcontrib-fancybox/>`_
