
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

::

    git clone https://github.com/sdpython/pyquickhelper.git
    cd pyquickhelper
    python setup.py install

.. _l-doctestunit:

Generate the setup
==================

Build the wheel
+++++++++++++++

To generate a zip or gz setup:

::

    python setup.py sdist --formats=gztar,zip

To generate a file *.whl:

::

    python setup.py bdist_wheel

Other available commands
++++++++++++++++++++++++

The setup implements other commands to help writing
code or testing notebooks.

.. runpython::
    :showcode:

    from pyquickhelper.pycode.setup_helper import get_available_setup_commands
    print("\n".join(sorted(get_available_setup_commands())))

The most used one is ``python setup.py clean_space``. The commands
modifies the files to be closer to :epkg:`pep8` conventions, it also
runs some checkings to display warnings for remaining issues.
The command ``python setup.py run_pylint`` runs :epkg:`pylint`
on the code. Extended syntax is
``python setup.py run_pylint <filter> <negative filte> -iXXXX``.
``-iXXXX`` ignores warnings *XXXX*. One must be added for each
warning to ignore. ``python setup.py buld_sphinx`` runs the
documentation, ``python setup.py copy27``, ``python setup.py run27``,
``python setup.py build27`` converts the module for Python 2.7
(not bullet proof), ``python setup.py history`` retrieves the
history and update file ``HISTORY.rst`` on root folder.

.. index:: notebooks, Jupyter Lab

``python setup.py notebook`` starts a local :epkg:`Jupyter`
notebook server to easily modify the notebooks, ``python setup.py lab``
does the same for :epkg:`Jupyter Lab`. Finally,
a script to start :epkg:`SciTe` with the right path
on :epkg:`Windows` (to be saved in ``something.bat``).

.. index:: SciTe

::

    @echo off

    set MYPYTHON=C:\Python36_x64
    set PYADDPATH=C:\username\GitHub
    set PATH=%MYPYTHON%;%PATH%
    set PYTHONPATH=%PYADDPATH%\pyquickhelper\src;%PYADDPATH%\pyensae\src;%PYADDPATH%\pyrsslocal\src;%PYADDPATH%\jyquickhelper\src
    set PYTHONPATH=%PYTHONPATH%;%PYADDPATH%\manydataapi\src;%PYADDPATH%\ensae_teaching_cs\src;%PYADDPATH%\mlinsights\src;%PYADDPATH%\mlstatpy\src
    set PYTHONPATH=%PYTHONPATH%;%PYADDPATH%\actuariat_python\src;%PYADDPATH%\code_beatrix\src;%PYADDPATH%\cpyquickhelper\src;%PYADDPATH%\ensae_projects\src
    set PYTHONPATH=%PYTHONPATH%;%PYADDPATH%\lightmlrestapi\src;%PYADDPATH%\lightmlboard\src;%PYADDPATH%\pandas_streaming\src;%PYADDPATH%\papierstat\src
    set PYTHONPATH=%PYTHONPATH%;%PYADDPATH%\pymmails\src;%PYADDPATH%\pysqllike\src;%PYADDPATH%\pymyinstall\src;%PYADDPATH%\teachpyx\src
    start /b pathtoscite\SciTE.exe

Unit tests
==========

It relies on :epkg:`pyquickhelper`.

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

The command line runs the unit tests.
The process ends with the code coverage (with module :epkg:`coverage`)
and publishes the report in folder `_doc/sphinxdoc/source/coverage`.
If options ``-e`` and ``-g`` are left empty, files containing `test_LONG_`,
`test_SKIP_`, `test_GUI_` in their
name are included. You can run them with a specific command:

::

    python setup.py unittests_LONG
    python setup.py unittests_SKIP
    python setup.py unittests_GUI

This was introduced to explicitely exclude long tests used to check a long process was not broken.
These commands do not accept parameters. Coverage reports are not merged.

Write and run one unit test
+++++++++++++++++++++++++++

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
    from pyquickhelper import fLOG

    # import the file you want to test
    from project_name.subproject.myexample import myclass

    class TestExample(unittest.TestCase):

        def test_split_cmp_command(self) :

            # to log information only when run as main file
            fLOG (__file__, self._testMethodName, OutputPrint = __name__ == "__main__")

            # you test content
            # it must raises an exception if a test fails.

    if __name__ == "__main__"  :
        unittest.main ()

You can check if the test is run on a specific environment:

::

    from pyquickhelper.pycode import skipif_travis, skipif_circleci
    from pyquickhelper.pycode import skipif_appveyor, skipif_azure

Function :ref:`is_travis_or_appveyor <pyquickhelper.pycode.ci_helper.is_travis_or_appveyor>` return a string
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
:epkg:`pep8` style. It will break it is not the case and will
indicate where it breaks. The code can be automatically modified
to follow that convention by running:

::

    python setup.py clean_space

The unit test `test_readme.py` checks the syntax of file `readme.rst`.
`PyPi <https://pypi.python.org/pypi>`_ runs on an older version of
:epkg:`docutils`. It checks this file follows this syntax.

The unit test `test_convert_notebooks.py` checks the syntax of every notebook
looks ok. This tests also removes all execution number and reformat the JSON.
It must be run before a commit if you add or modifies the notebook.
Removing the execution number makes it easy to compare two versions of the same
notebook.

Notebooks are not tested by default but they should wherever it is possible.
This can be done by using function
:func:`execute_notebook_list <pyquickhelper.ipythonhelper.run_notebook.execute_notebook_list>`.

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
This is what the following instruction based on Python 3 does.
The results will located in `dist_module27`.

::

    python setup.py copy27

From folder `dist_module27`, the unit test can be run he same way:

::

    python setup.py unittests

Or with :epkg:`nose`:

::

    nosetests.exe -w ut_<folder_name>

Documentation
=============

It relies on epkg:`pyquickhelper`.

.. _l-dependencies-tools:

Generation
++++++++++

The documentation can be written using `RST
<https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html>`_ format
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

* :epkg:`Sphinx`
* `pyquickhelper <https://pypi.python.org/pypi/pyquickhelper/>`_
* Required sphinx extensions can be found in the code of
  `set_sphinx_variables <pyquickhelper.helpgen.default_conf.set_sphinx_variables>`

As the documentation creates graphs to represent the dependencies,
Graphviz needs to be installed. Here is the list of required tools:

* `Python 64 bit <https://www.python.org/downloads/>`_
* :epkg:`7z`
* :epkg:`MiKTeX`
* :epkg:`Jenkins` (+ `GitHub <https://wiki.jenkins-ci.org/display/JENKINS/GitHub+Plugin>`_,
  `git <https://wiki.jenkins-ci.org/display/JENKINS/Git+Plugin>`_,
  `python <https://wiki.jenkins-ci.org/display/JENKINS/Python+Plugin>`_)
* :epkg:`pandoc`
* :epkg:`GIT` + :epkg:`GitHub`
* :epkg:`GraphViz`
* :epkg:`Inkscape`

If you need to use `Antlr <http://www.antlr.org/>`_:

* :epkg:`Java`

Jenkins extensions:

* `Build timeout plugin <https://wiki.jenkins-ci.org/display/JENKINS/Build-timeout+Plugin>`_
* `Collapsing Console Sections Plugin <https://wiki.jenkins-ci.org/display/JENKINS/Collapsing+Console+Sections+Plugin>`_
* `Console column plugin <https://wiki.jenkins-ci.org/display/JENKINS/Console+Column+Plugin>`_
* `Credentials Plugin <https://wiki.jenkins.io/display/JENKINS/Credentials+Plugin>`_
* `Extra Columns Plugin <https://wiki.jenkins-ci.org/display/JENKINS/Extra+Columns+Plugin>`_
* `Git <https://plugins.jenkins.io/git>`_
* `Next Executions <https://wiki.jenkins-ci.org/display/JENKINS/Next+Executions>`_
* `Text File <https://wiki.jenkins-ci.org/display/JENKINS/Text+File+Operations+Plugin>`_
* `Startup Trigger <https://wiki.jenkins.io/display/JENKINS/Startup+Trigger>`_: automatisation de build
* `Exclusive Execution <https://plugins.jenkins.io/exclusive-execution/>`_

The module will convert :epkg:`SVG` into images,
 it can handle :epkg:`javascript` with module
 :epkg:`js2py` and :epkg:`node.js`.

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

.. faqref::
    :title: List of Sphinx commands added by pyquickhelper
    :lid: f-sphinxext-pyq

    * :func:`bigger <pyquickhelper.sphinxext.sphinx_bigger_extension.bigger_role>`:
      to write with a custom size
    * :class:`blocref <pyquickhelper.sphinxext.sphinx_blocref_extension.BlocRef>`:
      to add a definition (or any kind of definition)
    * :class:`blocreflist <pyquickhelper.sphinxext.sphinx_blocref_extension.BlocRefList>`:
      to list all definitions
    * :class:`blogpost <pyquickhelper.sphinxext.sphinx_blog_extension.BlogPostDirective>`:
      to add a blog post, this command does not behave like the others,
      it should only be used in folder `_doc/sphinxdoc/source/blog`
    * :class:`blogpostagg <pyquickhelper.sphinxext.sphinx_blog_extension.BlogPostDirectiveAgg>`:
      to aggregate blog post, this should be manually added, the module
      *pyquickhelper* is preprocessing the documentation to produce pages containing such commands
    * :class:`cmdref <pyquickhelper.sphinxext.sphinx_cmdref_extension.CmdRef>`:
      to documentation a script the module makes available on the command line
    * :class:`cmdreflist <pyquickhelper.sphinxext.sphinx_cmdref_extension.CmdRefList>`:
      to list all commands
    * :func:`epkg <pyquickhelper.sphinxext.sphinx_epkg_extension.epkg_role>`:
      avoid repeating the same references in many places
    * :class:`exref <pyquickhelper.sphinxext.sphinx_exref_extension.ExRef>`:
      to add an example
    * :class:`exreflist <pyquickhelper.sphinxext.sphinx_exref_extension.ExRef>`:
      to list all example
    * :class:`faqref <pyquickhelper.sphinxext.sphinx_faqref_extension.FaqRef>`:
      to add a FAQ
    * :class:`faqreflist <pyquickhelper.sphinxext.sphinx_faqref_extension.FaqRefList>`:
      to list all FAQ
    * :class:`mathdef <pyquickhelper.sphinxext.sphinx_mathdef_extension.MathDef>`:
      to add a mathematical definition (or any kind of definition)
    * :class:`mathdeflist <pyquickhelper.sphinxext.sphinx_mathdef_extension.MathDefList>`:
      to list all definitions
    * :class:`nbref <pyquickhelper.sphinxext.sphinx_nbref_extension.NbRef>`:
      to add a magic command
    * :class:`nbreflist <pyquickhelper.sphinxext.sphinx_nbref_extension.NbRefList>`:
      to list all magic commands
    * :class:`runpython <pyquickhelper.sphinxext.sphinx_runpython_extension.RunPythonDirective>`:
      to run a script and display the output, it can be used to generate documentation
    * :class:`sharenet <pyquickhelper.sphinxext.sphinx_sharenet_extension.ShareNetDirective>`:
      to add buttons to share the page on a socal network
    * :class:`todoext <pyquickhelper.sphinxext.sphinx_todoext_extension.TodoExt>`:
      to add an issue or a work item
    * :class:`todoextlist <pyquickhelper.sphinxext.sphinx_todoext_extension.TodoExtList>`:
      to list all issues or work item

    These commands are documented in :ref:`l-sphinxextc`.

Notebooks
+++++++++

Notebooks in folder `_doc/notebooks` will be automatically
converted into *html*, *rst*, *pdf*, *slides* formats.
That requires latex and :epkg:`pandoc`.

.. _l-ci-jenkins:

Continuous Integration
======================

The module is tested with `Travis <https://travis-ci.com/sdpython/pyquickhelper>`_,
`AppVeyor <https://www.appveyor.com/>`_ and local testing with
:epkg:`Jenkins` for a exhaustive list of unit tests,
the documentation, the setup. Everything is fully tested on Windows
with the standard distribution and
:epkg:`Anaconda`. There are three builds definition:

* Travis: `.travis.yml <https://github.com/sdpython/pyquickhelper/blob/master/.travis.yml>`_
* AppVeyor: `appveyor.yml <https://github.com/sdpython/pyquickhelper/blob/master/appveyor.yml>`_
* Jenkins: `.local.jenkins.win.yml <https://github.com/sdpython/pyquickhelper/blob/master/.local.jenkins.win.yml>`_

The third file by processed by *pyquickhelper* itself to produce a series of Jenkins jobs
uploaded to a server. See :func:`setup_jenkins_server_yml <pyquickhelper.jenkinshelper.jenkins_helper.setup_jenkins_server_yml>`
to configurate a local Jenkins server.

When modules depend on others modules also being tested, the
unit tests and the documentation generation uses a local pypi server (port=8079).

Console Output
++++++++++++++

The plugin `Collapsing Sections Plugins <https://wiki.jenkins-ci.org/display/JENKINS/Collapsing+Console+Sections+Plugin>`_ can help parsing the output. The following section are added:

* ``---- JENKINS BEGIN UNIT TESTS ----``, * ``---- JENKINS END UNIT TESTS ----``
* ``---- JENKINS BEGIN DOCUMENTATION ----``, ``---- JENKINS END DOCUMENTATION ----``
* ``---- JENKINS BEGIN DOCUMENTATION NOTEBOOKS ----``, ``---- JENKINS END DOCUMENTATION NOTEBOOKS ----``
* ``---- JENKINS BEGIN DOCUMENTATION BLOG ----``, ``---- JENKINS END DOCUMENTATION BLOG ----``
* ``---- JENKINS BEGIN DOCUMENTATION COPY FILES ----``, ``---- JENKINS END DOCUMENTATION COPY FILES ----``
* ``---- JENKINS BEGIN DOCUMENTATION ENCODING ----``, ``---- JENKINS END DOCUMENTATION ENCODING ----``
* ``---- JENKINS BEGIN DOCUMENTATION SPHINX ----``, ``---- JENKINS END DOCUMENTATION SPHINX ----``
* ``---- JENKINS BEGIN WRITE VERSION ----``, ``---- JENKINS END WRITE VERSION ----``
* ``---- JENKINS BEGIN SETUPHOOK ----``, ``---- JENKINS END SETUPHOOK ----``
