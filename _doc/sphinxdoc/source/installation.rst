
.. _l-moreinstall:

Installation
============


    * Windows installation:
        * run the setup ``pyquickhelper*.win32.exe``
    * Windows installation with source:
        * download the file ``pyquickhelper*.tar.gz`` and unzip it
        * type the following commands::

            set PATH=%PATH%;c:\Python33
            python.exe setup.py install

    * Linux installation:
        * download the file ``pyquickhelper*.tar.gz``
        * type the following commands::

            tar xf pyquickhelper-py3.3.tar.gz
            sudo su
            python3.4 setup.py install

    * Using pip::

        pip install pyquickhelper

    If you install on `WinPython <http://winpython.sourceforge.net/>`_ distribution,
    you will need to add ``--pre`` to force the installation::

        pip install pyquickhelper --pre