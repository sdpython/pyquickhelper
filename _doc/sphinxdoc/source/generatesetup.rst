Generate the setup
==================

Unless you add an extension or some data to your module (images, text files),
no modification are required. To generate a zip or gz setup::

    %pythonexe% setup.py sdist --formats=gztar,zip

To generate a file *.whl* on Windows
(the module `wheel <https://pypi.python.org/pypi/wheel>`_ must be installed)::

    %pythonexe% setup.py bdist_wheel

