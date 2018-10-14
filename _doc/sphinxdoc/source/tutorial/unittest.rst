
Unit tests
==========

A couple of functions were implemented to automate
the unit test if the module follows the same design
as :epkg:`pyquickhelper`:

* The unit tests must be in ``<root>/_unittests``.
* There are only one level of subfolders inside this folder,
  all names are prefixed by ``ut_``.
* Tests files starts with ``test_``.
* Unit test must inherits from :*py:`unittest:TestCase` or
  :py:class:`ExtTestCase <pyquickhelper.pycode.unittestclass.ExtTestCase>`
  which adds a couple of *assert* methods.

One function is used to prints information but is disabled
when running the whole list of unit tests:
:func:`fLOG <pyquickhelper.loghelper.flog.fLOG>`.
Another function is often used to create a temporary folder
relative to the test file:
:func:`get_temp_folder <pyquickhelper.pycode.utils_tests_helper.get_temp_folder>`.
The option is prefered because it lets temporary data available
close to the code. It is easier to check if something went wrong.
Plus temporary files or folder are not always fully cleaned by the
operating system. A limit is sometimes reached and produces
an error difficult to interpret if the developer is not aware
of that limit.
Some behavior might change on continuous integration.
Function :func:`is_travis_or_appveyor <pyquickhelper.pycode.ci_helper.is_travis_or_appveyor>`
returns the continuous integration system used.
Finally, testing notebooks is important when there are many
and that's an important part of teachings.
The following function
:func:`test_notebook_execution_coverage <pyquickhelper.ipythonhelper.unittest_notebook.test_notebook_execution_coverage>`
tests a notebooks assuming it is in folder ``<root>/_docs/notebooks``.
It also keeps track of the number of executed cells and reports
on the coverage.
