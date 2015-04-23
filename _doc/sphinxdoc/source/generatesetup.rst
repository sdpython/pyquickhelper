Generate the setup
==================

Unless you add an extension or some data to your module (images, text files),
no modification are required. To generate a zip or gz setup::

    %pythonexe% setup.py sdist --formats=gztar,zip

To generate an executable setup on Windows::

    %pythonexe% setup.py clean_pyd
    %pythonexe% setup.py bdist_wininst

To generate a file *.msi* on Windows::

    %pythonexe% clean_pyd.py
    %pythonexe% setup.py bdist_msi

To generate a file *.whl* on Windows
(the module `wheel <https://pypi.python.org/pypi/wheel>`_ must be installed)::

    %pythonexe% clean_pyd.py
    %pythonexe% setup.py bdist_wheel

The first script removes all files ``.pyd`` which might cause some
issues if a setup for a different platform was generated.
To generate the setup for 64bit (it also works for the file *.msi*)::

    %pythonexe% setup.py clean_pyd
    %pythonexe% setup.py build bdist_wheel --plat-name=win-amd64

On Windows, the file ``build_setup_help_on_windows.bat`` does everything for you.
It also copies the documentation in folder ``dist``.
