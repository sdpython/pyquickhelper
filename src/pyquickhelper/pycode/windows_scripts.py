"""
@brief
@file Batch file use to automate some of the tasks (setup, unit tests, help, pypi).

.. versionadded:: 1.1
"""

#################
#: stop if error
#################
windows_error = "if %errorlevel% neq 0 exit /b %errorlevel%"

#################
#: prefix
#################
windows_prefix = """
if "%1"=="" goto default_value_python:
if "%1"=="default" goto default_value_python:
set pythonexe=%1
goto start_script:

:default_value_python:
set pythonexe=__PY34_X64__\\python
:start_script:
"""

#################
#: prefix 27
#################
windows_prefix_27 = """
if "%1"=="" goto default_value_python:
if "%1"=="default" goto default_value_python:
set pythonexe27=%1
goto start_script:

:default_value_python:
set pythonexe27=__PY27_X64__\\python
:start_script:
"""

#################
#: run unit test 27
#################
windows_unittest27 = """
set PYTHONPATH=
cd dist_module27\\_unittests

for /d %%d in (ut_*) do %pythonexe27%\\..\\Scripts\\nosetests.exe -w %%d

""" + windows_error + "\ncd ..\.."

#################
#: call the setup
#################
windows_setup = "%pythonexe% -u setup.py"
jenkins_windows_setup = "%jenkinspythonexe% -u setup.py"

#################
#: build script for Windows
#################
windows_build = """
IF EXIST dist del /Q dist\\*.*

set virtual_env_suffix=%2

if "%1"=="" goto default_value:
if "%1"=="default" goto default_value:
set pythonexe=%1
%pythonexe% setup.py write_version
goto custom_python:

:default_value:
IF NOT EXIST __PY34__ GOTO checkinstall64:

:checkinstall:
IF EXIST __PY34__vir%virtual_env_suffix% GOTO nexta:
mkdir __PY34__vir%virtual_env_suffix%

:nexta:
IF EXIST __PY34__vir%virtual_env_suffix%\\install GOTO fullsetupa:
__PY34__\\Scripts\\virtualenv __PY34__vir%virtual_env_suffix%\\install --system-site-packages
if %errorlevel% neq 0 exit /b %errorlevel%

:fullsetupa:
echo #######################################################0
__PY34__vir%virtual_env_suffix%\\install\\Scripts\\python -u setup.py install
if %errorlevel% neq 0 exit /b %errorlevel%
echo #######################################################1

:checkinstall64:
IF EXIST __PY34_X64__vir%virtual_env_suffix% GOTO nextb:
mkdir __PY34_X64__vir%virtual_env_suffix%

:nextb:
IF EXIST __PY34_X64__vir%virtual_env_suffix%\\install GOTO fullsetupb:
__PY34_X64__\\Scripts\\virtualenv __PY34_X64__vir%virtual_env_suffix%\\install --system-site-packages
if %errorlevel% neq 0 exit /b %errorlevel%

:fullsetupb:
echo #######################################################2
__PY34_X64__vir%virtual_env_suffix%\\install\\Scripts\\python -u setup.py install
if %errorlevel% neq 0 exit /b %errorlevel%
echo #######################################################3

:setup34:
IF NOT EXIST __PY34__ GOTO utpy34_64:
set pythonexe=__PY34__\\python
%pythonexe% setup.py write_version
%pythonexe% setup.py clean_pyd
%pythonexe% setup.py build bdist_wininst --plat-name=win-amd64
if %errorlevel% neq 0 exit /b %errorlevel%
echo #######################################################4

:utpy34_64:
set pythonexe=__PY34_X64__\\python
:custom_python:
echo ###----################################################5
if not exist ..\\virtual mkdir ..\\virtual
set virtual_env_py=..\\virtual\\__MODULE__
if not exist %pythonexe%\\..\\Scripts\\virtualenv.exe goto conda_virtual_env:

if exist %virtual_env_py%_vir%virtual_env_suffix% rmdir /Q /S %virtual_env_py%_vir%virtual_env_suffix%
mkdir %virtual_env_py%_vir%virtual_env_suffix%

if exist %virtual_env_py%_vir%virtual_env_suffix%\\python goto with_virtual:
set KEEPPATH=%PATH%
set PATH=%pythonexe%\\..;%PATH%
%pythonexe%\\..\\Scripts\\virtualenv --system-site-packages %virtual_env_py%_vir%virtual_env_suffix%
set PATH=%KEEPPATH%
if %errorlevel% neq 0 exit /b %errorlevel%
:with_virtual:
set pythonexe=%virtual_env_py%_vir%virtual_env_suffix%\\Scripts\\python
set pythonpip=%virtual_env_py%_vir%virtual_env_suffix%\\Scripts\\pip
goto requirements:

:conda_virtual_env:

if exist %virtual_env_py%_condavir%virtual_env_suffix% rmdir /Q /S %virtual_env_py%_condavir%virtual_env_suffix%

if exist %virtual_env_py%_condavir%virtual_env_suffix%\\python goto with_virtual_conda:
%pythonexe%\\..\\Scripts\\conda create -p %virtual_env_py%_condavir%virtual_env_suffix% --clone %pythonexe%\\.. --offline
if %errorlevel% neq 0 exit /b %errorlevel%
:with_virtual_conda:
set pythonexe=%virtual_env_py%_condavir%virtual_env_suffix%\\python
set pythonpip=%virtual_env_py%_condavir%virtual_env_suffix%\\Scripts\\pip

:requirements:
echo #######################################################_auto_setup_dep.py
cd build\\auto_setup
..\\..\\%pythonexe% auto_setup_dep.py install
if %errorlevel% neq 0 exit /b %errorlevel%
cd ..\\..

echo #######################################################_requirements_begin
echo %pythonpip%
__REQUIREMENTS__
if %errorlevel% neq 0 exit /b %errorlevel%
echo #######################################################_requirements_end

%pythonexe% setup.py write_version
echo #######################################################_clean
%pythonexe% -u setup.py clean_space
if %errorlevel% neq 0 exit /b %errorlevel%
echo #######################################################_unit
%pythonexe% -u setup.py unittests
if %errorlevel% neq 0 exit /b %errorlevel%
echo #######################################################6

%pythonexe% setup.py clean_pyd
%pythonexe% setup.py sdist --formats=gztar,zip --verbose
if %errorlevel% neq 0 exit /b %errorlevel%
%pythonexe% setup.py bdist_wininst --plat-name=win-amd64
if %errorlevel% neq 0 exit /b %errorlevel%
%pythonexe% setup.py bdist_msi
if %errorlevel% neq 0 exit /b %errorlevel%
%pythonexe% setup.py bdist_wheel
if %errorlevel% neq 0 exit /b %errorlevel%
echo #######################################################7

:documentation:
%pythonexe% -u setup.py build_sphinx
if %errorlevel% neq 0 exit /b %errorlevel%
echo #######################################################8

:copyfiles:
if not exist dist\\html mkdir dist\\html
xcopy /E /C /I /Y _doc\\sphinxdoc\\build\\html dist\\html
if exist _doc\\sphinxdoc\\build\\latex xcopy /E /C /I /Y _doc\\sphinxdoc\\build\\latex\\*.pdf dist\\html
if %errorlevel% neq 0 exit /b %errorlevel%

:end:
rem we copy the wheel on a local folder to let a pypiserver take it
if not exist ..\\local_pypi_server mkdir ..\\local_pypi_server
copy /Y dist\\*.whl ..\\local_pypi_server
"""

####################################################
#: build any script for Windows from a virtual environment
####################################################
windows_any_setup_command = """
if "%1"=="" echo usage: SCRIPT command [pythonpath] [suffix]

IF EXIST dist del /Q dist\\*.*

set script_command=%1
set virtual_env_suffix=%3

if "%2"=="" goto default_value:
if "%2"=="default" goto default_value:
set pythonexe=%2
%pythonexe% setup.py write_version
goto custom_python:

:default_value:
set pythonexe=__PY34_X64__\\python

:custom_python:
echo ###----################################################5
if not exist ..\\virtual mkdir ..\\virtual
set virtual_env_py=..\\virtual\\__MODULE__
if not exist %pythonexe%\\..\\Scripts\\virtualenv.exe goto conda_virtual_env:

if exist %virtual_env_py%_vir%virtual_env_suffix% rmdir /Q /S %virtual_env_py%_vir%virtual_env_suffix%
mkdir %virtual_env_py%_vir%virtual_env_suffix%

if exist %virtual_env_py%_vir%virtual_env_suffix%\\python goto with_virtual:
set KEEPPATH=%PATH%
set PATH=%pythonexe%\\..;%PATH%
%pythonexe%\\..\\Scripts\\virtualenv --system-site-packages %virtual_env_py%_vir%virtual_env_suffix%
set PATH=%KEEPPATH%
if %errorlevel% neq 0 exit /b %errorlevel%
:with_virtual:
set pythonexe=%virtual_env_py%_vir%virtual_env_suffix%\\Scripts\\python
set pythonpip=%virtual_env_py%_vir%virtual_env_suffix%\\Scripts\\pip
goto requirements:

:conda_virtual_env:

if exist %virtual_env_py%_condavir%virtual_env_suffix% rmdir /Q /S %virtual_env_py%_condavir%virtual_env_suffix%

if exist %virtual_env_py%_condavir%virtual_env_suffix%\\python goto with_virtual_conda:
%pythonexe%\\..\\Scripts\\conda create -p %virtual_env_py%_condavir%virtual_env_suffix% --clone %pythonexe%\\.. --offline
if %errorlevel% neq 0 exit /b %errorlevel%
:with_virtual_conda:
set pythonexe=%virtual_env_py%_condavir%virtual_env_suffix%\\python
set pythonpip=%virtual_env_py%_condavir%virtual_env_suffix%\\Scripts\\pip

:requirements:
echo #######################################################_auto_setup_dep.py
cd build\\auto_setup
%pythonexe% auto_setup_dep.py install
if %errorlevel% neq 0 exit /b %errorlevel%
cd ..\\..

echo #######################################################_requirements_begin
echo %pythonpip%
__REQUIREMENTS__
if %errorlevel% neq 0 exit /b %errorlevel%
echo #######################################################_requirements_end

%pythonexe% setup.py write_version
echo #######################################################_clean
%pythonexe% -u setup.py clean_space
if %errorlevel% neq 0 exit /b %errorlevel%
echo #######################################################_unit
%pythonexe% -u setup.py %script_command%
if %errorlevel% neq 0 exit /b %errorlevel%
echo #######################################################6

"""

#################
#: notebooks
#################
windows_notebook = """
if "%1"=="" goto default_value:
if "%1"=="default" goto default_value:
set pythonexe=%1
goto nextn:

:default_value:
set pythonexe=__PY34_X64__

:nextn:
set path=%path%;%pythonexe%;%pythonexe%\\Scripts
ipython3 notebook --notebook-dir=_doc\\notebooks --matplotlib=inline
"""

#################
#: publish a module
#################
windows_publish = """
%pythonexe% setup.py rotate --match=.zip --keep=1
%pythonexe% setup.py rotate --match=.tar.gz --keep=3
rem %pythonexe% setup.py sdist register
%pythonexe% setup.py sdist --formats=gztar upload
"""

#################
#: publish the documentation
#################
windows_publish_doc = """
%pythonexe% -u setup.py upload_docs --upload-dir=dist/html
"""

#################
#: run a pypi server
#################
windows_pypi = """
set pythonexe=__PY34_X64__

:custom_python:
if "%2"=="" goto default_port:
if "%2"=="default" goto default_port:
set portpy=%2
goto run:

:default_port:
set portpy=__PORT__

:run:
%pythonexe%\Scripts\pypi-server.exe -u -p %portpy% --disable-fallback ..\\local_pypi_server
"""

#################
#: script for Jenkins
#################
windows_jenkins = "set jenkinspythonexe=__PYTHON__\n" + jenkins_windows_setup + " build_script\n" + \
    windows_error + "\nauto_unittest_setup_help.bat %jenkinspythonexe% __SUFFIX__\n" + \
    windows_error

windows_jenkins_any = "set jenkinspythonexe=__PYTHON__\n" + jenkins_windows_setup + " build_script\n" + \
    windows_error + "\nauto_cmd_any_setup_command.bat __COMMAND__ %jenkinspythonexe% __SUFFIX__\n" + \
    windows_error

####################
#: script for Jenkins 27
####################
windows_jenkins_unittest27 = """
set CURRENT_PATH=%WORKSPACE%
set virtual_env_py=%CURRENT_PATH%\\..\\virtual\\__MODULE__
if exist %virtual_env_py%_conda27vir rmdir /Q /S %virtual_env_py%_conda27vir
%jenkinspythonexe%\\..\\Scripts\\conda create -p %virtual_env_py%_conda27vir --clone %jenkinspythonexe%\\.. --offline
if %errorlevel% neq 0 exit /b %errorlevel%
set jenkinspythonexe=%virtual_env_py%_conda27vir\\python
set jenkinspythonpip=%virtual_env_py%_conda27vir\\Scripts\\pip

:requirements:
echo #######################################################_auto_setup_dep.py
cd build\\auto_setup
..\\..\\%jenkinspythonexe% auto_setup_dep.py install
if %errorlevel% neq 0 exit /b %errorlevel%
cd ..\\..
%jenkinspythonpip% install --extra-index-url http://localhost:__PORT__/simple/ pyquickhelper
if %errorlevel% neq 0 exit /b %errorlevel%

echo #######################################################_requirements_begin
echo %jenkinspythonpip%
"""


windows_jenkins_27 = [
    "set jenkinspythonexe=__PYTHON__\n" + jenkins_windows_setup + " build_script\n" +
    windows_error + "\nauto_setup_copy27.bat %jenkinspythonexe%\n" +
    windows_error,
    "set jenkinspythonexe=__PYTHON27__\n\n" +
    windows_jenkins_unittest27 +
    "\n\n__REQUIREMENTS__\n\n" +
    "\nauto_cmd_run27.bat %jenkinspythonexe%\n" + windows_error,
    "set jenkinspythonexe=__PYTHON27__\n" +
    "set CURRENT_PATH=%WORKSPACE%\n" +
    "set virtual_env_py=%CURRENT_PATH%\\..\\virtual\\__MODULE__\n" +
    "set jenkinspythonexe=%virtual_env_py%_conda27vir\\python\n" +
    "\nauto_cmd_build27.bat %jenkinspythonexe%\n" + windows_error,
    "copy dist_module27\\dist\\*.whl ..\\local_pypi_server"]

##################
#: auto setup
##################
setup_script_dependency_py = """
import sys
from distutils.core import setup, Extension
import distutils.sysconfig as SH
from setuptools import find_packages

project_var_name = "dependencies___MODULE__"
versionPython = "%s.%s" % (sys.version_info.major, sys.version_info.minor)
path = "Lib/site-packages/" + project_var_name

setup(
    name=project_var_name,
    version=versionPython,
    install_requires=[
        "numpy",
        "dateutils",
        "IPython",
        "matplotlib",
        "sphinx",
        "pandas",
        "docutils", ],
)
"""
#########################
#: copy27
#########################

copy_dist_to_local_pypi = """
if not exist ..\local_pypi_server mkdir ..\local_pypi_server
copy /Y dist\*.whl ..\local_pypi_server
"""

###############
#: blog post
###############
windows_blogpost = """
%pythonexe% auto_rss_server.py
"""

#####################
#: documenation server
#####################
windows_docserver = """
%pythonexe% auto_doc_server.py
"""
