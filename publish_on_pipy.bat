if "%1"=="" goto default_value:
set pythonexe=%1\python
goto custom_python:

:default_value:
set pythonexe=c:\Python34_x64\python

:custom_python:
%pythonexe% setup.py rotate --match=.zip -k 0
%pythonexe% setup.py rotate --match=.tar.gz -k 5
rem %pythonexe% setup.py sdist register
%pythonexe% setup.py sdist upload --formats=gztar