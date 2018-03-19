
=======
History
=======

1.7.9999 (2018-12-31)
=====================

**Bugfix**

* `102`: fix sphinx command line ``-j 1`` becomes ``-j1``
* `103`: fix import issue for Sphinx 1.7.1 (released on 2/23/2017)
* `104`: implement visit, depart for pending_xref and rst translator
* `106`: replace pdflatex by xelatex to handle utf-8 characters
* `108`: add command lab, creates a script to start jupyter lab on notebook folder
* `113`: propose a fix for a bug introduced by pip 9.0.2,
  see :ref:`pip 9.0.2 and issue with pip._vendor.urllib3.contrib <blog-pip-vendor-urllib3-contrib>`

**Features**

* `107`: convert svg into png for notebook snippets
* `112`: allow to set custom snippets for notebooks

1.6.2413 (2018-02-14)
=====================

**Bugfix**

* `86`: avoids last line of notebooks in rst to disappear
* `95`: fix replaced unicode characters in latex output
* `99`: fix issue with subfolders in example galleries
* `96`: better handling of notebooks for latex
* `101`: update to Sphinx 1.7

**Features**

* `73`: merges coverage reports from differents jobs about unit tests
* `84`: remove *epkg* instruction in call_cli_function
* `92`: add directive *video* for sphinx documentation
* `93`: add a variable in documentation configuration for custom replacements
  in notebooks
* `94`: implements test fixture ``@skipif_appveyor``, ``@skipif_travis``,
  ``@skipif_circleci``
* `100`: fix indentation in documented source files

1.5.2275 (2017-11-28)
=====================

**Bugfix**

* `46`: update to Sphinx 1.6
* `54`: fix searchbox for `sphinx_rtd_theme <https://github.com/rtfd/sphinx_rtd_theme>`_
* `69`: overwrites toctree to catch exception and process rst inline
* `71`: skip old notebook execution when computing the coverage

**Features**

* `56`: support function for role epkg
* `36`: add support for sphinx-gallery
* `53`: handle history, converts the file into something usable by module releases
* `52`: add coverage for notebooks
* `61`: add a build on `circleci <https://circleci.com/gh/sdpython/pyquickhelper>`_,
  builds the documentation, populates the artifacts section
* `63`: add file_detail in *get_repo_log*
* `60`: add notebook coverage as a separate page
* `34`: applies pep8 on the code being rendered on the documentation
* `65`: add function to clean readme.rst before sending it to pypi
* `67`: add toctree delayed which gets filled after the dynamic content is created, use it for blogs
* `77`: add class ExtUnitCase with extensive test function
* `78`: get_temp_folder change other default directory
* `81`: add youtube sphinx extension

1.4.1000 (2016-01-01)
=====================
