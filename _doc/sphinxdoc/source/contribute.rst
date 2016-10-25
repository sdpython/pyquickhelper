
==========
Contribute
==========

.. contents::
    :local:


.. _l-moreinstall:

Installation
============


Installation with pip
+++++++++++++++++++++

  ::

    pip install pyquickhelper
    
Installation with the source
++++++++++++++++++++++++++++

If you want to contribute, 
you need to fork and clone this reposity
`sdpython/pyquickhelper <https://github.com/sdpython/pyquickhelper>`_.
Otherwise, a zip file of the sources is enough.

.. _l-doctestunit:


Generate the setup
==================

To generate a zip or gz setup:

::

    python setup.py sdist --formats=gztar,zip

To generate a file *.whl:

::

    python setup.py bdist_wheel
    

Unit tests
==========

It relies on `pyquickhelper <https://pypi.python.org/pypi/pyquickhelper/>`_.

Run unit tests
++++++++++++++

You need to get the sources and run:

::

    python -u setup.py unittests
    
There are more options.

* ``[-d seconds]``: run all unit tests for which predicted duration is below a given threshold.
* ``[-f file]``: run all unit tests in file (do not use the full path)
* ``[-e regex]``: run all unit tests files matching the regular expression (can be combined with ``-g``)
* ``[-g regex]``: run all unit tests files not matching the regular expression

You can get them with:

::

    python setup.py unittests --help

The process first calls the function :func:`_setup_hook <pyquickhelper._setup_hook>`. 
It can be used to initialize the module even if it is most of the time unused.
The process ends the code coverage (with module `coverage <https://coverage.readthedocs.io/en/coverage-4.2/>`_)
and publishes the report in folder `_doc/sphinxdoc/source/coverage`.
If options ``-e`` and ``-g`` are left empty, files containing `test_LONG_`, `test_SKIP_`, `test_GUI_` in their
name are included. You can run them with a specific command:

::

    python setup.py unittests_LONG
    python setup.py unittests_SKIP
    python setup.py unittests_GUI

This was introduced to explicitely exclude long tests used to check a long process was not broken.
These commands do not accept parameters. Coverage reports are not merged.


Run one unit test
+++++++++++++++++

All unit tests must follow the convention: 

::

    _unittests/ut_<subfolder>/test_<filename>.py

This test file must begin by `test_` and must look like the following::

    """
    @file
    @brief  test log(time=2s)
    """
    import sys
    import os
    import unittest

    # to import files from the module
    # and to make sure we do not use another installed version 
    try :
        import src
    except ImportError :
        path = os.path.normpath(os.path.abspath( os.path.join( os.path.split(__file__)[0], "..", "..")))
        if path not in sys.path : sys.path.append (path)
        import src

    from pyquickhelper import fLOG

    # import the file you want to test
    from src.project_name.subproject.myexample import myclass

    class TestExample (unittest.TestCase):

        def test_split_cmp_command(self) :

            # to log information
            fLOG (__file__, self._testMethodName, OutputPrint = __name__ == "__main__")

            # you test content
            # it must raises an exception if a test fails.
            
    if __name__ == "__main__"  :
        unittest.main ()
        
You can check if the test is run on a specific environment:

::

    from pyquickhelper.pycode import is_travis_or_appveyor
    
Function :ref:`is_travis_or_appveyor <pyquickhelper.pycode.is_travis_or_appveyor>` return a string
``'travis'`` or ``'appveyor'`` is the code is executed on such environment or None if
none of them is detected.
You can create a temporary folder next to the test file by running:

::

    from pyquickhelper.pycode import get_temp_folder
    temp = get_temp_folder(__file__, "temp_<name>")
    
This folder is automatically removed if it exists
when the function is called.

Specific unit tests
+++++++++++++++++++

The unit test `test_flake8.py` ensures all the code follows the
`pep8 <https://www.python.org/dev/peps/pep-0008/>`_ style.
It will break it is not the case and will indicate where it breaks.
The code can be automatically modified to follow that convention
by running:

::

    python setup.py clean_space

The unit test `test_readme.py` checks the syntax of file `readme.rst`.
`PyPi <https://pypi.python.org/pypi>`_ runs on an older version of 
`docutils <http://docutils.sourceforge.net/>`_. 
It checks this file follows this syntax.

The unit test `test_convert_notebooks.py` checks the syntax of every notebook
looks ok. This tests also removes all execution number and reformat the JSON.
It must be run before a commit if you add or modifies the notebook.
Removing the execution number makes it easy to compare two versions of the same
notebook.

Notebooks are not tested by default but they should wherever it is possible.
This can be done by using function 
:func:`execute_notebook_list <pyquickhelper.ipythonhelper.run_notebook.execute_notebook_list>`_.

    
        
Use passwords
+++++++++++++

If a couple of unit test requires a login and a password 
to test FTP functionalities for example,
you should get them with `keyring <https://pypi.python.org/pypi/keyring>`_.

::

    import keyring
    keyring.get_password("something", os.environ["COMPUTERNAME"] + "user")
    
You can set the password by running only once:

::

    import keyring
    keyring.set_password("something", os.environ["COMPUTERNAME"] + "user", "...")
    keyring.set_password("something", os.environ["COMPUTERNAME"] + "pwd", "...")


.. _generatedoc:


Python 2.7
++++++++++

The sources can not be used with Python 2.7. The syntax first needs to be converted.
That what does the following instruction based on Python 3.
The results will located in `dist_module27`.

::

    python setup.py copy27
    
From folder `dist_module27`, the unit test can be run he same way:

::

    python setup.py unittests
    
Or with `nose <https://pypi.python.org/pypi/nose>`_:

::

    nosetests.exe -w ut_<folder_name>
    


Documentation
=============

It relies on `pyquickhelper <https://pypi.python.org/pypi/pyquickhelper/>`_.

Generation
++++++++++


The documentation can be written using `RST <http://sphinx-doc.org/rest.html>`_ format
or `javadoc <http://en.wikipedia.org/wiki/Javadoc>`_ format. The documentation
can generated by:

::

    python setup.py build_sphinx
    
It requires the full sources from GitHub and not only the installed package which does not 
contains the documentation.
It will go through the following steps:

* It gets a version number from `git <https://git-scm.com/>`_ (the sources must be on `git <https://git-scm.com/>`_).
* It will copy all files found in `src` in folder `_doc/sphinxdoc/source/[project_name]`.
* It will generates a file *.rst* for each python file in `_doc/sphinxdoc/source/[project_name]`.
* It will run the generation of the documentation using Sphinx.
* Notebooks can be placed in `_doc/notebooks`, they will be added to the documentation.
* It will generated aggregated pages for blog posts added to 
  `_doc/sphinxdoc/source/blog/YYYY/<anything>.rst`.

The results are stored in folder `_doc/sphinxdoc/build`.
The process requires dependencies:

* `Sphinx <http://sphinx-doc.org/>`_
* `pyquickhelper <https://pypi.python.org/pypi/pyquickhelper/>`_
* Required sphinx extensions can be found in the code of 
  `set_sphinx_variables <pyquickhelper.helpgen.default_conf.set_sphinx_variables>`

As the documentation creates graphs to represent the dependencies,
Graphviz needs to be installed. Here is the list of required tools:

* `Python 64 bit <https://www.python.org/downloads/>`_
* `7zip <http://www.7-zip.org/>`_
* `Miktex <http://miktex.org/>`_
* `Jenkins <https://jenkins-ci.org/>`_ (+ `GitHub <https://wiki.jenkins-ci.org/display/JENKINS/GitHub+Plugin>`_, 
  `git <https://wiki.jenkins-ci.org/display/JENKINS/Git+Plugin>`_, 
  `python <https://wiki.jenkins-ci.org/display/JENKINS/Python+Plugin>`_, 
  `pipeline <https://wiki.jenkins-ci.org/display/JENKINS/Build+Pipeline+Plugin>`_)
* `pandoc <http://pandoc.org/>`_
* `Git <http://git-scm.com/>`_ + `GitHub <https://github.com/>`_
* `GraphViz <http://www.graphviz.org/>`_
* `InkScape <https://inkscape.org/en/>`_

If you need to use `Antlr <http://www.antlr.org/>`_:

* `Java <http://www.java.com/fr/download/>`_



Configuration
+++++++++++++

.. literalinclude:: conf.py


Write documentation
+++++++++++++++++++

The documentation is organized as follows:

* `src/<module_name>`: contains the sources of the modules
* `_doc/notebooks`: contains the notebooks included in the documentation
* `_doc/sphinxdoc/source`: contains the sphinx documentation
* `_doc/sphinxdoc/blog/YYYY`: contains the blog posts for year `YYYY`

When the documentation is being generated,
the sources are copied into `pyquickhelper/_unittests/_doc/sphinxdoc/source/pyquickhelper`.
The documentation can be in `javadoc <http://en.wikipedia.org/wiki/Javadoc>`_ 
format is replaced by the RST syntax. Various
files are automatically generated (indexes, examples, FAQ).
Then `sphinx <http://sphinx-doc.org/>`_ is run.

You will find some examples of custom sphinx commands
in :ref:`l-example-documentation`.

.. faqref:: List of Sphinx commands added by pyquickhelper?

    * :ref:`bigger <pyquickhelper.sphinxext.sphinx_bigger_extension.bigger_role>`: 
      to write with a custom size
    * :ref:`blocref <pyquickhelper.sphinxext.sphinx_blocref_extension.BlocRef>`: 
      to add a definition (or any kind of definition)
    * :ref:`blocreflist <pyquickhelper.sphinxext.sphinx_blocref_extension.BlocRefList>`: 
      to list all definitions
    * :ref:`blogpost <pyquickhelper.sphinxext.sphinx_blog_extension.>`: 
      to add a blog post, this command does not behave like the others,
      it should only be used in folder `_doc/sphinxdoc/source/blog`
    * :ref:`blogpostagg <pyquickhelper.sphinxext.sphinx_blog_extension.>`: 
      to aggregate blog post, this should be manually added, the module 
      *pyquickhelper* is preprocessing the documentation to produce pages containing such commands
    * :ref:`exref <pyquickhelper.sphinxext.sphinx_exref_extension.ExRef>`: 
      to add an example
    * :ref:`exreflist <pyquickhelper.sphinxext.sphinx_exref_extension.ExRef>`: 
      to list all example
    * :ref:`faqref <pyquickhelper.sphinxext.sphinx_faqref_extension.FaqRef>`: 
      to add a FAQ
    * :ref:`faqreflist <pyquickhelper.sphinxext.sphinx_faqref_extension.FaqRefList>`: 
      to list all FAQ
    * :ref:`mathdef <pyquickhelper.sphinxext.sphinx_mathdef_extension.MathDef>`: 
      to add a mathematical definition (or any kind of definition)
    * :ref:`mathdeflist <pyquickhelper.sphinxext.sphinx_mathdef_extension.MathDefList>`: 
      to list all definitions
    * :ref:`nbref <pyquickhelper.sphinxext.sphinx_nbref_extension.NbRef>`: 
      to add a magic command 
    * :ref:`nbreflist <pyquickhelper.sphinxext.sphinx_nbref_extension.NbRefList>`: 
      to list all magic commands
    * :ref:`runpython <pyquickhelper.sphinxext.sphinx_runpython_extension.RunPythonDirective>`: 
      to run a script and display the output, it can be used to generate documentation
    * :ref:`sharenet <pyquickhelper.sphinxext.sphinx_sharenet_extension.ShareNetDirective>`: 
      to add buttons to share the page on a socal network
    * :ref:`todoext <pyquickhelper.sphinxext.sphinx_todoext_extension.TodoExt>`: 
      to add an issue or a work item
    * :ref:`todoextlist <pyquickhelper.sphinxext.sphinx_todoext_extension.TodoExtList>`: 
      to list all issues or work item 
    

Notebooks
+++++++++

Notebooks in folder `_doc/notebooks` will be automatically
converted into *html*, *rst*, *pdf*, *slides* formats. 
That requires latex and `pandoc <http://pandoc.org/>`_.


.. _l-ci-jenkins:


Continuous Integration
======================

The module is tested with `Travis <https://travis-ci.org/sdpython/pyquickhelper>`_, 
`AppVeyor <https://www.appveyor.com/>`_ and local testing with
`Jenkins <https://jenkins-ci.org/>`_ for a exhaustive list of unit tests,
the documentation, the setup. Everything is fully tested on Windows with the standard distribution and 
`Anaconda <http://continuum.io/downloads>`_.
There are three builds definition:

* Travis: `.travis.yml <https://github.com/sdpython/pyquickhelper/blob/master/.travis.yml>`_
* AppVeyor: `appveyor.yml <https://github.com/sdpython/pyquickhelper/blob/master/appveyor.yml>`_
* Jenkins: `.local.jenkins.win.yml <https://github.com/sdpython/pyquickhelper/blob/master/.local.jenkins.win.yml>`_

The third file by processed by *pyquickhelper* itself to produce a series of Jenkins jobs
uploaded to a server. See :func:`setup_jenkins_server_yml <pyquickhelper.jenkinshelper.jenkins_helper.setup_jenkins_server_yml>`
to configurate a local Jenkins server.

When modules depend on others modules also being tested, the 
unit tests and the documentation generation uses a local pypi server (port=8079).

