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

Get the list of files in a SVN repository and copy them in another folder::

    all = []
    action = synchronize_folder (folder1, folder2, svn1 = True, 
                            operations = lambda a,b,c : all.append (a))
    for a in all :
        print (a)
        
And to copy them::        

    synchronize_folder (folder1, folder2, svn1 = True)
    
A logging function which does not break due to encoding issues::

    fLOG(OutputPrint=True)  # enable the printing
    fLOG(something)         # prints the date + the something
    
To generate the documentation for this project::

    generate_help_sphinx("pyquickhelper")

It assumes this function is run a script from the root folder.
It copies every all the files in ``_doc/sphinxdoc/source``.

Design
------

This project contains various helper about logging functions, unit tests and help generation.
   * a source folder: ``src``
   * a unit test folder: ``_unittests``, go to this folder and run ``run_unittests.py``
   * a _doc folder: ``_doc``, it will contains the documentation
   * a file ``setup.py`` to build and to install the module
   * a file ``make_help.py`` to build the sphinx documentation


