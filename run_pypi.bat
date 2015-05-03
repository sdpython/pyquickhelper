echo off
IF EXIST dist del /Q dist\*.*

if "%1"=="" goto default_value:
set pythonexe="%1"
%pythonexe% setup.py write_version
goto custom_python:

:default_value:
set pythonexe=c:\Python34_x64

:custom_python:
if "%2"=="" goto default_port:
set portpy=%2
goto run:

:default_port:
set portpy=8067

:run:
echo on
%pythonexe%\Scripts\pypi-server.exe -u -p %portpy% --disable-fallback .