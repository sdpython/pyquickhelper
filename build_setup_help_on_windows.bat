rem we remove everything from dist
echo off
del /Q dist\*.*

rem unittests with python 3.4

IF NOT EXIST c:\Python34 GOTO checkinstall64:

:checkinstall:
IF EXIST c:\Python34vir GOTO nexta:
mkdir c:\Python34vir

:nexta:
IF EXIST c:\Python34vir\install GOTO fullsetupa:
c:\Python34\Scripts\virtualenv c:\Python34vir\install --system-site-packages
if %errorlevel% neq 0 exit /b %errorlevel%

:fullsetupa:
echo #######################################################
c:\Python34vir\install\Scripts\python -u setup.py install
if %errorlevel% neq 0 exit /b %errorlevel%
echo #######################################################


:checkinstall64:
IF EXIST c:\Python34_64vir GOTO nextb:
mkdir c:\Python34_64vir

:nextb:
IF EXIST c:\Python34_64vir\install GOTO fullsetupb:
c:\Python34\Scripts\virtualenv c:\Python34_64vir\install --system-site-packages
if %errorlevel% neq 0 exit /b %errorlevel%

:fullsetupb:
echo #######################################################
c:\Python34_64vir\install\Scripts\python -u setup.py install
if %errorlevel% neq 0 exit /b %errorlevel%
echo #######################################################

:utpy34:
IF NOT EXIST c:\Python34 GOTO utpy33_64:
set pythonexe="c:\Python34\python"
%pythonexe% -u setup.py clean_space
if %errorlevel% neq 0 exit /b %errorlevel%
%pythonexe% -u setup.py unittests
if %errorlevel% neq 0 exit /b %errorlevel%
echo #######################################################

:utpy33_64:
IF NOT EXIST c:\Python33_x64 GOTO utpy33:
set pythonexe="c:\Python33_x64\python"
%pythonexe% clean_pyd.py
%pythonexe% setup.py build bdist_wininst --plat-name=win-amd64
if %errorlevel% neq 0 exit /b %errorlevel%
echo #######################################################

:utpy33:
IF NOT EXIST c:\Python33 GOTO utpy34_64:
set pythonexe="c:\Python33\python"
%pythonexe% clean_pyd.py
%pythonexe% setup.py sdist --formats=gztar,zip --verbose
if %errorlevel% neq 0 exit /b %errorlevel%
%pythonexe% setup.py bdist_wininst
if %errorlevel% neq 0 exit /b %errorlevel%
echo #######################################################

:utpy34_64:
set pythonexe="c:\Python34_x64\python"
%pythonexe% clean_pyd.py
%pythonexe% setup.py build bdist_wininst --plat-name=win-amd64
if %errorlevel% neq 0 exit /b %errorlevel%
%pythonexe% setup.py build bdist_msi --plat-name=win-amd64
if %errorlevel% neq 0 exit /b %errorlevel%
echo #######################################################

:setup_msi:
set pythonexe="c:\Python34_x64\python"
%pythonexe% clean_pyd.py
%pythonexe% setup.py sdist --formats=gztar,zip --verbose
if %errorlevel% neq 0 exit /b %errorlevel%
%pythonexe% setup.py bdist_wininst
if %errorlevel% neq 0 exit /b %errorlevel%
%pythonexe% setup.py bdist_msi
if %errorlevel% neq 0 exit /b %errorlevel%
echo #######################################################

:documentation:
%pythonexe% -u setup.py build_sphinx
if %errorlevel% neq 0 exit /b %errorlevel%
echo #######################################################

:copyfiles:
if not exist dist\html mkdir dist\html
xcopy /E /C /I /Y _doc\sphinxdoc\build\html dist\html
if %errorlevel% neq 0 exit /b %errorlevel%