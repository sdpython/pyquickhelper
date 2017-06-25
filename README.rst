
.. _l-README:

README
======

.. image:: https://travis-ci.org/sdpython/pyquickhelper.svg?branch=master
    :target: https://travis-ci.org/sdpython/pyquickhelper
    :alt: Build status

.. image:: https://ci.appveyor.com/api/projects/status/t2g9olcgqgdvqq3l?svg=true
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

.. image:: https://api.codacy.com/project/badge/Grade/793ffca6089d4d02b8292a50df74a8a4
    :target: https://www.codacy.com/app/sdpython/pyquickhelper?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=sdpython/pyquickhelper&amp;utm_campaign=Badge_Grade
    :alt: Codacy Badge

**Links:**

* `GitHub/pyquickhelper <https://github.com/sdpython/pyquickhelper>`_
* `documentation <http://www.xavierdupre.fr/app/pyquickhelper/helpsphinx/index.html>`_
* `Blog <http://www.xavierdupre.fr/app/pyquickhelper/helpsphinx/blog/main_0000.html#ap-main-0>`_

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
