Generate the setup
==================

Unless you add an extension or some data to your module (images, text files),
no modification are required. To generate a zip or gz setup::

    %pythonexe% setup.py sdist --formats=gztar,zip

To generate a file *.whl* on Windows
(the module `wheel <https://pypi.python.org/pypi/wheel>`_ must be installed)::

    %pythonexe% setup.py bdist_wheel

To generate an executable setup on Windows::

    %pythonexe% setup.py bdist_wininst

To generate a file *.msi* on Windows::

    %pythonexe% setup.py bdist_msi

To generate the setup for 64bit (it also works for the file *.msi*)::

    %pythonexe% setup.py build bdist_wininst --plat-name=win-amd64

