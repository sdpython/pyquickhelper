
.. image:: https://github.com/sdpython/pyquickhelper/blob/master/_doc/sphinxdoc/source/phdoc_static/project_ico.png?raw=true
    :target: https://github.com/sdpython/pyquickhelper/

.. _l-README:

pyquickhelper: automation of many things
========================================

.. image:: https://travis-ci.com/sdpython/pyquickhelper.svg?branch=master
    :target: https://app.travis-ci.com/github/sdpython/pyquickhelper/
    :alt: Build status

.. image:: https://ci.appveyor.com/api/projects/status/t2g9olcgqgdvqq3l?svg=true
    :target: https://ci.appveyor.com/project/sdpython/pyquickhelper
    :alt: Build Status Windows

.. image:: https://circleci.com/gh/sdpython/pyquickhelper/tree/master.svg?style=svg
    :target: https://circleci.com/gh/sdpython/pyquickhelper/tree/master

.. image:: https://dev.azure.com/xavierdupre3/pyquickhelper/_apis/build/status/sdpython.pyquickhelper
    :target: https://dev.azure.com/xavierdupre3/pyquickhelper/

.. image:: https://badge.fury.io/py/pyquickhelper.svg
    :target: https://pypi.org/project/pyquickhelper/

.. image:: https://img.shields.io/badge/license-MIT-blue.svg
    :alt: MIT License
    :target: http://opensource.org/licenses/MIT

.. image:: https://codecov.io/github/sdpython/pyquickhelper/coverage.svg?branch=master
    :target: https://codecov.io/github/sdpython/pyquickhelper?branch=master

.. image:: http://img.shields.io/github/issues/sdpython/pyquickhelper.png
    :alt: GitHub Issues
    :target: https://github.com/sdpython/pyquickhelper/issues

.. image:: https://app.codacy.com/project/badge/Grade/9d73a6712fb24e2fa404b3e33c6201ac
    :target: https://www.codacy.com/gh/sdpython/pyquickhelper/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=sdpython/pyquickhelper&amp;utm_campaign=Badge_Grade
    :alt: Codacy Badge

.. image:: http://www.xavierdupre.fr/app/pyquickhelper/helpsphinx/_images/nbcov.png
    :target: http://www.xavierdupre.fr/app/pyquickhelper/helpsphinx/all_notebooks_coverage.html
    :alt: Notebook Coverage

.. image:: https://pepy.tech/badge/pyquickhelper/month
    :target: https://pepy.tech/project/pyquickhelper/month
    :alt: Downloads

.. image:: https://img.shields.io/github/forks/sdpython/pyquickhelper.svg
    :target: https://github.com/sdpython/pyquickhelper/
    :alt: Forks

.. image:: https://img.shields.io/github/stars/sdpython/pyquickhelper.svg
    :target: https://github.com/sdpython/pyquickhelper/
    :alt: Stars

.. image:: https://img.shields.io/github/repo-size/sdpython/pyquickhelper
    :target: https://github.com/sdpython/pyquickhelper/
    :alt: size

`pyquickhelper <http://www.xavierdupre.fr/app/pyquickhelper/helpsphinx/index.html>`_
is used to automate the release of the documentation such as automating *Jenkins*,
converting notebooks into many formats, extending *Sphinx* with custom
extensions... It assumes the project is organized on the same template
as this one.

Functionalities
---------------

* simple forms in notebooks
* help generation including notebook conversion
* folder synchronization
* logging
* help running unit tests
* simple server to server sphinx documentation
* file compression, zip, gzip, 7z
* helpers for ipython notebooks (upgrade, offline run)
* parser to quickly add a magic command in a notebook
* Sphinx directives to integrate a blogpost in the documentation
* mechanism to add forms in notebooks

Design
------

This project contains the following folders:

* a source folder: *src*
* a unit test folder: *_unittests*, go to this folder and run *run_unittests.py*
* a folder: *_doc*, it will contain the documentation, a subfolder *_doc/sphinxdox/source/blog* contains blog post
  to communicate on the module
* a file *setup.py* to build and to install the module, if the source were retrieve from GitHub,
  the script can also be called with the following extra options (*python setup.py <option>*):
  * clean_space: remove extra spaces in the code
  * build_sphinx: builds the documentation
  * unittests: run the unit tests, compute the code coverage
* a script *build_script.bat* which produces many script on Windows to easily run the setup,
  generate the documentation, run the unit tests.

Examples
--------

Convert a notebook into slides:

::

    from pyquickhelper.helpgen import nb2slides
    nb2slides("nb.ipynb", "convert.slides.html")

Merge two notebooks:

::

    from pyquickhelper.ipythonhelper import read_nb
    nb1 = read_nb("<file1>", kernel=False)
    nb2 = read_nb("<file2>", kernel=False)
    nb1.merge_notebook(nb2)
    nb1.to_json(outfile)

Run a notebook:

::

    from pyquickhelper.ipythonhelper import run_notebook
    run_notebook("source.ipynb", working_dir="temp",
                outfilename="modified.ipynb",
                additional_path = [ "c:/temp/mymodule/src" ] )

Run a command line program:

::

    from pyquickhelper.loghelper import run_cmd
    out,err = run_cmd("python setup.py install", wait=True)

A sphinx extension to generate python documentation from a script:

::

    .. runpython::
        :showcode:

        import sys
        print("sys.version_info=", str(sys.version_info))

Links
-----

* `GitHub/pyquickhelper <https://github.com/sdpython/pyquickhelper>`_
* `documentation <http://www.xavierdupre.fr/app/pyquickhelper/helpsphinx/index.html>`_
* `Blog <http://www.xavierdupre.fr/app/pyquickhelper/helpsphinx/blog/main_0000.html#ap-main-0>`_

.. image:: https://mybinder.org/badge_logo.svg
    :target: https://mybinder.org/v2/gh/sdpython/pyquickhelper/master
    :alt: Binder
