.. _l-doctestunit:

Documentation, unit tests, setup
================================


The instruction ``python setup.py build_script`` generates
many short scripts to run simple tasks such as running unit tests,
generating the setup, the documentation, running a pipy server, 
publishing the setup or the documentation,
gathering blogs from the web site this documentation is deployed...



Unit tests
----------

The project includes an easy to write and run unit tests:
    * the file ``_unittests/run_unittests.py`` runs all of them.
    * you can add a new one in a folder: ``_unittests/<subfolder>/test_<filename>.py``.

This test file must begin by ``test_`` and must look like the following::

    """
    @brief      test log(time=1s)

    You should indicate a time in seconds. The program ``run_unittests.py``
    will sort all test files by increasing time and run them.
    """

    import sys, os, unittest

    # to import files from the module
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
        
Passwords
---------

A couple of unit test requires a login and a password 
to test FTP functionalities. It should look like the following:

::

    import keyring
    keyring.set_password("web", os.environ["COMPUTERNAME"] + "user", "...")
    keyring.set_password("web", os.environ["COMPUTERNAME"] + "pwd", "...")
