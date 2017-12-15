
=======
History
=======

1.6.9999 (2018-12-31)
=====================

**BugFix**

* `86`: avoids last line of notebooks in rst to disappear

**Features**

* `84`: remove *epkg* instruction in call_cli_function

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
