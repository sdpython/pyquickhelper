Generate the setup
==================

Unless you add an extension or some data to your module (images, text files),
no modification are required. To generate a zip or gz setup::

    %pythonexe% setup.py sdist --formats=gztar,zip
    
To generate an executable setup on Windows::

    %pythonexe% clean_pyd.py
    %pythonexe% setup.py bdist_wininst
    
The first script removes all files ``.pyd`` which might cause some 
issues if a setup for a different platform was generated.
To generate the setup for 64bit::

    %pythonexe% clean_pyd.py
    %pythonexe% setup.py build bdist_wininst --plat-name=win-amd64


On Windows, the file ``build_setup_help_on_windows.bat`` does everything for you.
It also copies the documentation in folder ``dist``.
