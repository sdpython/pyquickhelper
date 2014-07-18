rem we remove everything from dist
echo off
del /Q dist\*.*

rem unittests with python 3.4

set pythonexe="c:\Python34\python"
%pythonexe% -u setup.py unittests

rem python 3.3

set pythonexe="c:\Python33_x64\python"
%pythonexe% clean_pyd.py
%pythonexe% setup.py build bdist_wininst --plat-name=win-amd64

set pythonexe="c:\Python33\python"
%pythonexe% clean_pyd.py
%pythonexe% setup.py sdist --formats=gztar,zip --verbose
%pythonexe% setup.py bdist_wininst

rem python 3.4

set pythonexe="c:\Python34_x64\python"
%pythonexe% clean_pyd.py
%pythonexe% setup.py build bdist_wininst --plat-name=win-amd64
%pythonexe% setup.py build bdist_msi --plat-name=win-amd64

set pythonexe="c:\Python34\python"
%pythonexe% clean_pyd.py
%pythonexe% setup.py sdist --formats=gztar,zip --verbose
%pythonexe% setup.py bdist_wininst
%pythonexe% setup.py bdist_msi

rem help

%pythonexe% -u setup.py build_sphinx

if not exist dist\html mkdir dist\html
xcopy /E /C /I /Y _doc\sphinxdoc\build\html dist\html


