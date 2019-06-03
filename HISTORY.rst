
.. _l-HISTORY:

=======
History
=======

current - 2019-06-04 - 0.00Mb
=============================

* `251`: Switch to Sphinx 2.1, remove specific code for older versions (2019-06-03)
* `250`: fix errors introduced by installing sphinx 2.1 (2019-06-03)

1.9.3135 - 2019-05-27 - 2.04Mb
==============================

* `238`: add simple function to profile and command line, implements a graph as well (2019-05-27)
* `248`: add option numpy_precision in runpython (2019-05-05)

1.9.3118 - 2019-04-26 - 2.04Mb
==============================

* `247`: Use of command in setup.py (2019-04-25)
* `246`: Supports projects without src folder (2019-04-25)

1.9.3100 - 2019-04-06 - 2.04Mb
==============================

* `245`: make test pass for sphinx 2.0.0 (2019-03-30)

1.9.3069 - 2019-03-25 - 2.04Mb
==============================

* `244`: remove need of __init__.py in folder src, do not import conf.py in the same process while generating the documentation (2019-03-25)
* `243`: refactor unit tests (2019-03-20)
* `242`: add command line sphinx_rst to convert rst document (2019-03-16)
* `239`: add sphinx directive to add date of the latest commit (2019-03-16)
* `240`: replaces separator ; by ;; in yaml files when dealing with conditional instructions (2019-03-04)
* `236`: command line is slow (2019-03-01)
* `237`: add parameter number_format to df2rst (2019-02-28)
* `235`: removes FutureWarning when using ExtTestClass (2019-02-24)
* `234`: fix RSS stream (2019-02-21)

1.8.2973 - 2019-02-16 - 2.03Mb
==============================

* `233`: add a function to run all test function in a file (2019-02-14)
* `232`: Missing blog posts between two pages (2019-01-28)
* `230`: autosignature does not work for C++ function in cpyquickhelper (2019-01-19)
* `229`: remove specific code for python2 (2019-01-12)
* `228`: fix missing jpg images in documentation (2019-01-09)
* `227`: makes more functions available from command line (2019-01-08)
* `226`: fix command line name when created from a function (2019-01-08)
* `225`: add class BufferedPrint to retrieve logging through fLOG (2019-01-07)
* `224`: add process_notebooks in the list of function available through the command line (2019-01-06)
* `223`: jenkins script: distringuish between script and linux instruction if (2019-01-04)
* `222`: update jenkins job cleanup options (2019-01-03)
* `221`: ignore errors when combining reports (2019-01-02)
* `220`: creates a GUI for the command line window (2018-12-31)
* `219`: Add default negative pattern when cleaning files in a folder (2018-12-31)
* `217`: remove unnecessary logging when generating sphinx documentation (2018-12-20)
* `216`: conversion of notebook including svg fails (2018-12-18)
* `215`: add quote_node for quotations (sphinx) (2018-12-18)
* `214`: fix issue with neg_pattern in explore_folder_iterfile (2018-12-11)
* `213`: removes cmdref from documentation when creating a parser for a function (2018-12-10)
* `212`: issue when the default value is None when building the parser for a specific function (2018-12-09)
* `211`: automatically git tag when publishing (2018-12-05)
* `210`: add __main__ command line (2018-11-29)
* `209`: implements function retrieve_notebooks_in_folder (2018-11-25)
* `208`: update to azure CI (2018-11-25)
* `205`: Slides conversion are missing from the documentation (2018-11-09)
* `204`: Fix missing snippet for notebook when it fails finding one (2018-11-06)
* `203`: make epkg links anonymous to avoid warning about duplicated target (2018-11-05)
* `202`: make runpython keep context from one execution to the next one (2018-11-01)
* `201`: handle language options in runpython and rst builder (2018-11-01)
* `200`: ignore issue E402 when applying autopep8 (move import at the top of the file) (2018-10-28)
* `199`: better logging in synchronisation_folder (2018-10-14)
* `198`: broken links in the documentation (magic command ,example) (2018-10-14)
* `197`: do not raise exception if latex is not found when using rst2html (2018-10-06)
* `196`: add function add_rst_links to automatically add links into one string (2018-10-04)
* `195`: implement a doctree outputter (2018-09-19)
* `194`: check why call an extension from the setup is different from adding it to the list of extensions (2018-09-19)
* `193`: fix an issue when converting a werzeug object into string (2018-09-17)
* `192`: resolve issues with image and sphinx (2018-09-16)
* `191`: implement latex custom builder for rst2html (2018-09-16)
* `190`: Take dependency on Sphinx >= 1.8 (2018-09-13)
* `189`: fix import issue with update to Sphinx 1.8.0 (2018-09-13)
* `188`: add supports for images in rst and md writers (2018-09-12)
* `187`: fix bug in doxypy when class definition is followed by a commentary (2018-09-12)
* `186`: remove <SYSTEM MESSAGE> for role ref when converting a string rst into html or rst (2018-09-08)
* `185`: add markdown rst converter (2018-09-08)
* `184`: add tag :orphan: to additional files (2018-09-08)
* `183`: use svg image for formula in HTML and png in latex (2018-08-27)
* `182`: implementation of a backup plan if downloading require.js fails (2018-08-27)
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
