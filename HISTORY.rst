
.. _l-HISTORY:

=======
History
=======

current - 2018-08-25 - 0.00Mb
=============================

* `181`: fix an issue when combining coverage_report after the unit tests passed (2018-08-24)
* `180`: add parameter persistent to get_temp_folder (2018-08-24)
* `179`: put a default value for neg_pattern if it is none to avoid known folders (function check_pep8) (2018-08-23)
* `178`: add parameter delay to wait between two files being transferred through FTP (2018-08-23)
* `177`: remove ping helper (2018-08-20)
* `163`: fix automation for Jenkins on linux (2018-08-20)
* `32`: add command local_jenkins for setup.py (2018-08-20)
* `176`: add margin around toggle button (sphinx) (2018-08-19)
* `175`: removes output title if toggle option is used (2018-08-19)
* `174`: changes runpython titles into <<< and >>> (2018-08-19)
* `173`: add option current to runpython to run a script in the folder of the source file which contains it (2018-08-19)
* `172`: rst2html: parameters directives allows single directive with no new nodes (2018-08-19)
* `171`: allow a class to modify the script to run in runpython sphinx directive (2018-08-18)
* `170`: add option syspath for autosignature (2018-08-05)
* `169`: add option debug to autosignature (2018-08-05)
* `168`: documentation does not produce a page for a compiled module in pure C++ (not with pybind11) (2018-08-05)
* `166`: fix github link when link points to a compile module (2018-08-05)
* `167`: autosignature fails for function implemented in pure C++ (not with pybind11) (2018-08-04)
* `165`: documentation does not automatically generate .rst for module written in C (2018-08-04)
* `164`: improve autosignature for builtin function (2018-08-03)
* `162`: reduce the impact of RuntimeError: Kernel died before replying to kernel_info (2018-07-29)

1.8.2673 - 2018-07-28 - 1.99Mb
==============================

* `161`: fix unit test test_build_script on appveyor (2018-07-28)
* `160`: notebook server remains open if an exception happens during the execution (2018-07-25)
* `159`: fix a bug with pylint version (2018-07-23)
* `158`: replaces clock by perf_counter (2018-07-22)
* `156`: fix issue with update to python-jenkins 1.1.0 (2018-07-22)
* `155`: fix issue with pylint 2.0 (2018-07-22)
* `154`: notebook coverage add color (2018-05-27)
* `153`: fix message "do not understand why t1 >= t2 for file %s" % full (2018-05-27)
* `151`: bug in autosignature, shorten path does not work for static method (2018-05-24)
* `150`: hide warnings produced by add_missing_development_version (2018-05-23)
* `149`: modifies autosignature to display the shortest import way (2018-05-19)
* `148`: fix unit test test_changes_graph (pandas update) (2018-05-17)
* `146`: remove raise ... (...) from e in setup.py (2018-05-17)
* `145`: add a script to launch scite on windows with the right path (2018-05-13)

1.8.2602 - 2018-05-11 - 1.98Mb
==============================

* `144`: disable sphinx gallery extension if no example (2018-05-11)
* `143`: add setup option to run pylint (2018-05-11)
* `142`: look for the files which makes pylint crash on Windows (2018-05-11)
* `141`: check_pep8 does not detect line too long and unused variables (use of pylint) (2018-05-11)

1.7.2581 - 2018-05-07 - 2.00Mb
==============================

* `140`: modify assertEqualArray to allow small different (assert_almost_equal) (2018-05-07)
* `138`: retrieve past issues in history.rst (2018-05-06)
* `139`: update to python-jenkins 1.0.0 (2018-05-05)
* `137`: fix bug in bug HTML output (aggregated pages) (2018-04-29)
* `136`: add parameter create_dest to synchronize_folder (2018-04-29)
* `135`: fix for sphinx 1.7.3 (circular reference) (2018-04-22)
* `134`: allow url in video sphinx extension (2018-04-22)
* `133`: add a collapsible container, adapt it for runpython (2018-04-22)
* `132`: catch warning in run_python_script output, use redirect_stdout (2018-04-21)
* `131`: remove warning in runpython (2018-04-21)
* `130`: add plot output for runpython (2018-04-21)
* `129`: implement an easy way to profile a function in unit test (2018-04-19)
* `128`: fix issue in enumerate_pypi_versions_date (2018-04-14)
* `127`: update to pip 10 (many API changes) (2018-04-14)
* `126`: remove dependency on flake8, use pycodestyle (2018-04-13)
* `125`: fix sharenet for rst format (2018-04-05)
* `124`: add CodeNode in rst builder (2018-04-05)
* `123`: fix style for blogpostagg, remove inserted admonition (2018-04-05)
* `122`: fix notebook name when converting into rst (collision with html) (2018-04-05)
* `121`: extend list of functions in ExtTestCase (NotEqual, Greater(strict=True), NotEmpty (2018-04-01)
* `120`: add _fieldlist_row_index if missing in HTMLTranslatorWithCustomDirectives (2018-04-01)
* `119`: collision with image names in notebooks converted into rst (2018-03-29)
* `117`: bug with nbneg_pattern, check unit test failing due to that (2018-03-26)
* `116`: add tag .. raw:: html in notebook converted into rst (2018-03-26)
* `114`: automatically builds history with release and issues + add command history in setup (2018-03-24)
* `111`: enable manual snippet for notebook, repace add_notebook_menu by toctree in sphinx (2018-03-20)
* `113`: propose a fix for a bug introduced by pip 9.0.2 (2018-03-19)
* `112`: allow to set custom snippets for notebooks (2018-03-15)
* `109`: run javascript producing svg and convert it into png (2018-03-15)
* `107`: convert svg into png for notebook snippets (2018-03-12)
* `108`: add command lab, creates a script to start jupyter lab on notebook folder (2018-03-10)
* `106`: replace pdflatex by xelatex to handle utf-8 (2018-03-03)
* `104`: implement visit, depart for pending_xref and rst translator (2018-03-01)
* `103`: fix import issue for Sphinx 1.7.1 (2018-03-01)
* `102`: fix sphinx command line (2018-02-24)

1.6.2413 - 2018-02-13 - 1.98Mb
==============================

* `100`: fix indentation when copying the sources in documentation repository (2018-02-04)
* `99`: bug with galleries of examples with multiple subfolders (2018-01-30)

1.5.2275 - 2017-11-28 - 0.50Mb
==============================

1.4.1533 - 2016-09-10 - 0.36Mb
==============================
