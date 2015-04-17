echo off
IF EXIST dist del /Q dist\*.*

if "%1"=="" goto default_value:
set pythonexe27="%1"
goto py34:

:default_value:
set pythonexe27=c:\Anaconda2\python

:py34:
if "%2"=="" goto default_value34:
set pythonexe34="%2"
goto utpy34:

:default_value34:
set pythonexe34=c:\Python34_x64\python


:utpy34:
%pythonexe34% setup.py copy27
if %errorlevel% neq 0 exit /b %errorlevel%
set PYTHONPATH=
cd dist_module27\_unittests

for /d %%d in (ut_*) do %pythonexe27%\..\Scripts\nosetests.exe -w %%d

if %errorlevel% neq 0 exit /b %errorlevel%
echo #######################################################
cd ..

rem we add the script with publish the module for python 2.7
echo %pythonexe27% setup.py bdist_wheel upload > publish_on_pipy27.bat

:setup27_x64_msi_wheel:
%pythonexe27% setup.py bdist_wheel
if %errorlevel% neq 0 exit /b %errorlevel%
echo #######################################################
cd ..
if not exist dist: mkdir dist
copy dist_module27\dist\*.whl dist

rem
rem autopep8
rem coverage
rem flake8
rem wheel