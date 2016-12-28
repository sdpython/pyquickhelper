
.. blogpost::
    :title: Frequent commands and automation
    :keywords: command line, batch files
    :date: 2015-05-06
    :categories: automation, setup

    The script ``setup.py`` accepts several options
    such as ``install`` or ``build``. It also accepts
    ``unittest`` to run the unit tests or ``build_sphinx``
    to build the documentation.
    It usually requires to have a command line windows opened
    as well as an editor to write programs.
    On Windows, the module now produces a series of scripts
    to automate tasks such as running the unit tests,
    building the documentation. They are not included in the sources
    anymore but the can be obtained by typing::

        python setup.py build_script

    The scripts can now be produced for every module
    using pyquickhelper to automate setup, unit tests and
    documentation.
