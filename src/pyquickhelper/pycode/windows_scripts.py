"""
@brief
@file Batch file use to automate some of the tasks (setup, unit tests, help, pypi).
"""
import sys


def _sversion():
    return "PY%d%d" % sys.version_info[:2]

#################
#: stop if error
#################


windows_error = "if %errorlevel% neq 0 exit /b %errorlevel%"

#################
#: prefix
#################
windows_prefix = """
@echo off
@echo SCRIPT: windows_prefix
if "%1"=="" goto default_value_python:
if "%1"=="default" goto default_value_python:
set pythonexe=%1
goto start_script:

:default_value_python:
set pythonexe=__PY??_X64__\\python

@echo ~SET pythonexe=%pythonexe%

:start_script:
set current=%~dp0
if EXIST %current%setup.py goto current_is_setup:
set current=%current%..\\
cd ..
if EXIST %current%setup.py goto current_is_setup:
@echo Unable to find %current%setup.py
exit /b 1

:current_is_setup:
@echo ~SET current=%current%

""".replace("PY??", _sversion())

#################
#: prefix 27
#################
windows_prefix_27 = """
@echo off
@echo SCRIPT: windows_prefix_27
if "%1"=="" goto default_value_python:
if "%1"=="default" goto default_value_python:
set pythonexe27=%1
goto start_script:

:default_value_python:
set pythonexe27=__PY27_X64__\\python
:start_script:
@echo PY27: ~SET pythonexe27=%pythonexe27%
"""

#################
#: run unit test 27
#################
windows_unittest27 = """
@echo off
@echo SCRIPT: windows_unittest27
set PYTHONPATH=
@echo run27: ~SET PYTHONPATH=
@echo pythonexe27=%pythonexe27%
set current=%~dp0
cd %current%..\\dist_module27\\_unittests

@echo run27: check existing for nose in %pythonexe27%\\..\\Scripts\\nosetests.exe
if NOT EXIST %pythonexe27%\\..\\Scripts\\nosetests.exe dir %pythonexe27%\\..\\Scripts

rem errorlevel does not work well in a loop
rem for /d %%d in (ut_*) do (
rem     @echo ~CALL %pythonexe27%\\..\\Scripts\\nosetests.exe -w %%d
rem     %pythonexe27%\\..\\Scripts\\nosetests.exe -w %%d
rem     if %errorlevel% neq 0 exit /b %errorlevel%
rem )

@echo run27: start the loop

rem we are in a virtual environnement
@echo if not exist %pythonexe27%\\..\\Scripts set pythonexe27=%pythonexe27%\\..\\..\\Scripts
if not exist %pythonexe27%\\..\\Scripts set pythonexe27=%pythonexe27%\\..\\..\\Scripts
@echo looking for nosetests.exe in %pythonexe27%

__LOOP_UNITTEST_FOLDERS__

""" + windows_error + "\ncd ..\\.."

############
#: copy to local pypiserver
############

copy_to_pypiserver = """
@echo SCRIPT: copy_to_pypiserver
@echo ~LABEL end
rem we copy the wheel on a local folder to let a pypiserver take it
if not exist ..\\..\\local_pypi mkdir ..\\..\\local_pypi
if not exist ..\\..\\local_pypi\\local_pypi_server mkdir ..\\..\\local_pypi\\local_pypi_server
@echo ~CALL if exist dist copy /Y dist\\*.whl ..\\..\\local_pypi\\local_pypi_server
if exist dist copy /Y dist\\*.whl ..\\..\\local_pypi\\local_pypi_server
"""

####################################################
#: build any script for Windows from a virtual environment
####################################################
windows_any_setup_command_base = """

set current=%~dp0
if EXIST %current%setup.py goto current_is_setup:
set current=%current%..\\
cd ..
if EXIST %current%setup.py goto current_is_setup:
@echo Unable to find %current%setup.py
exit /b 1

:current_is_setup:
@echo ~SET current=%current%

@echo SCRIPT: windows_any_setup_command_base
@echo off
if "%1"=="" @echo usage: SCRIPT [pythonpath] [suffix] [command] [...]
set CURRENT_THIS=%~dp0

if EXIST %current%setup.py goto current_is_setup:
set current=%current%..\\
cd ..
if EXIST %current%setup.py goto current_is_setup:
@echo Unable to find %current%setup.py
exit /b 1

:current_is_setup:
@echo ~SET CURRENT_THIS=%CURRENT_THIS%

IF EXIST dist del /Q dist\\*.*
IF EXIST build del /Q build\\*.*

if "%2"=="" goto default_value_suffix:
if "%2"=="default" goto default_value_suffix:
set virtual_env_suffix=%2
goto default_value_suffix_next:
:default_value_suffix:
set virtual_env_suffix=_anyenv
:default_value_suffix_next:
@echo ~SET set virtual_env_suffix=%virtual_env_suffix%

if "%1"=="" goto default_value:
if "%1"=="default" goto default_value:
set pythonexe=%1
goto default_value_next:
:default_value:
set pythonexe=__PY??_X64__\\python
:default_value_next:

echo ###----################################################5
echo ###----################################################5
echo ###----################################################5
echo %pythonexe%
echo ###----################################################5
echo ###----################################################5
echo ###----################################################5
SET ROOT_VIRTUAL_ENV=%CURRENT_THIS%_virtualenv
if not exist %ROOT_VIRTUAL_ENV% mkdir %ROOT_VIRTUAL_ENV%
set virtual_env_py=%ROOT_VIRTUAL_ENV%\\__MODULE__
@echo ~SET virtual_env_py=%ROOT_VIRTUAL_ENV%\\__MODULE__
if not exist %pythonexe%\\..\\Scripts\\virtualenv.exe goto conda_virtual_env:

if exist %virtual_env_py%_vir%virtual_env_suffix% rmdir /Q /S %virtual_env_py%_vir%virtual_env_suffix%
mkdir %virtual_env_py%_vir%virtual_env_suffix%

if exist %virtual_env_py%_vir%virtual_env_suffix%\\python goto with_virtual:
set KEEPPATH=%PATH%
@echo ~SET KEEPPATH=%PATH%
set PATH=%pythonexe%\\..;%PATH%
@echo ~SET PATH=%pythonexe%\\..;%PATH%
@echo ~CALL %pythonexe%\\..\\Scripts\\virtualenv --system-site-packages %virtual_env_py%_vir%virtual_env_suffix%
%pythonexe%\\..\\Scripts\\virtualenv --system-site-packages %virtual_env_py%_vir%virtual_env_suffix%
@echo ### VIRTUAL ENVIRONMENT CREATED in %virtual_env_py%_vir%virtual_env_suffix%

@echo on
rem _PATH_VIRTUAL_ENV_
@echo off

:with_virtual:
@echo ~LABEL with_virtual
set pythonexe=%virtual_env_py%_vir%virtual_env_suffix%\\Scripts\\python
@echo ~SET pythonexe=%virtual_env_py%_vir%virtual_env_suffix%\\Scripts\\python
set pythonpip=%virtual_env_py%_vir%virtual_env_suffix%\\Scripts\\pip
@echo ~SET pythonpip=%virtual_env_py%_vir%virtual_env_suffix%\\Scripts\\pip
goto requirements:

:conda_virtual_env:
@echo ~LABEL conda_virtual_env
if exist %virtual_env_py%_condavir%virtual_env_suffix% rmdir /Q /S %virtual_env_py%_condavir%virtual_env_suffix%

if exist %virtual_env_py%_condavir%virtual_env_suffix%\\python goto with_virtual_conda:

@echo ~CALL %pythonexe%\\..\\Scripts\\conda create -p %virtual_env_py%_condavir%virtual_env_suffix% --clone %pythonexe%\\.. --offline
%pythonexe%\\..\\Scripts\\conda create -p %virtual_env_py%_condavir%virtual_env_suffix% --clone %pythonexe%\\.. --offline
if %errorlevel% neq 0 exit /b %errorlevel%

:with_virtual_conda:
@echo ~LABEL with_virtual_conda
set pythonexe=%virtual_env_py%_condavir%virtual_env_suffix%\\python
@echo ~SET pythonexe=%virtual_env_py%_condavir%virtual_env_suffix%\\python
set pythonpip=%virtual_env_py%_condavir%virtual_env_suffix%\\Scripts\\pip
@echo ~SET pythonpip=%virtual_env_py%_condavir%virtual_env_suffix%\\Scripts\\pip
%pythonpip% install sphinx --upgrade --cache-dir=%virtual_env_py%_condavir%virtual_env_suffix%
@echo ~%pythonpip% install sphinx --upgrade --cache-dir=%virtual_env_py%_condavir%virtual_env_suffix%

:requirements:
@echo #######################################################_auto_setup_dep.py
cd build\\auto_setup
set pythonexe_rel=..\\..\\%pythonexe%.exe
@echo ~SET pythonexe_rel=..\\..\\%pythonexe%.exe
if exist %pythonexe_rel% goto auto_setup_relpath:
set pythonexe_rel=%pythonexe%
@echo ~SET pythonexe_rel=%pythonexe%

:auto_setup_relpath:
@echo ~LABAL auto_setup_relpath
@echo ~CALL %pythonexe_rel% auto_setup_dep.py install
%pythonexe_rel% auto_setup_dep.py install > auto_setup_dep.log
rem if %errorlevel% neq 0 exit /b %errorlevel%
rem we continue to run the script even if it seems to fail
cd ..\\..
@echo #######################################################_auto_setup_dep.py END

@echo #######################################################_requirements_begin
@echo ~SET %pythonpip%
__REQUIREMENTS__
if %errorlevel% neq 0 exit /b %errorlevel%
@echo #######################################################_requirements_end
%pythonpip% freeze
@echo #######################################################_requirements_list

@echo ~SET pythonexe=%pythonexe%
@echo ~CALL %pythonexe% %current%setup.py write_version
%pythonexe% %current%setup.py write_version
if %errorlevel% neq 0 exit /b %errorlevel%
@echo ################# VERSION
more %~dp0..\\version.txt
if %errorlevel% neq 0 exit /b %errorlevel%
@echo ################# VERSION

@echo #######################################################_PATH
set PYTHONPATH=%PYTHONPATH%;%current%\\src__ADDITIONAL_LOCAL_PATH__;%current%__ADDITIONAL_LOCAL_PATH__
@echo ~SET PYTHONPATH=%PYTHONPATH%;%current%\\src__ADDITIONAL_LOCAL_PATH__;%current%__ADDITIONAL_LOCAL_PATH__
""".replace("PY??", _sversion())


#################
#: setup_hook for Windows
#################

windows_setup_hook = """
@echo SCRIPT: windows_setup_hook
@echo #######################################################_setup_hook
@echo ~CALL %pythonexe% %current%setup.py setup_hook
%pythonexe% %current%setup.py setup_hook
if %errorlevel% neq 0 exit /b %errorlevel%
@echo #######################################################_END_BASE
"""

#################
#: build script for Windows
#################

windows_any_setup_command = windows_any_setup_command_base + windows_setup_hook + """
@echo ~CALL %pythonexe% -u %current%setup.py %3 %4 %5 %6 %7 %8 %9
rem set PYTHONPATH=additional_path
%pythonexe% -u %current%setup.py %3 %4 %5 %6 %7 %8 %9
if %errorlevel% neq 0 exit /b %errorlevel%
@echo #######################################################6
""" + copy_to_pypiserver

#################
#: call the setup
#################
windows_setup = "rem set PYTHONPATH=additional_path\n%pythonexe% -u %current%setup.py"
jenkins_windows_setup = "%jenkinspythonexe% -u %current%setup.py"

#################
#: build setup script for Windows
#################

windows_build_setup = windows_any_setup_command_base + windows_setup_hook + """
@echo ~CALL %pythonexe% %current%setup.py sdist %2 --formats=gztar,zip --verbose
%pythonexe% %current%setup.py sdist %2 --formats=gztar,zip --verbose
if %errorlevel% neq 0 exit /b %errorlevel%
pushd %current%
@echo ~CALL %pythonexe% %current%setup.py bdist_wheel %2
%pythonexe% %current%setup.py bdist_wheel %2
popd
if %errorlevel% neq 0 exit /b %errorlevel%
""" + copy_to_pypiserver

#################
#: build script MAIN SCRIPT
#################
windows_build = windows_any_setup_command_base + windows_setup_hook + """
@echo #######################################################_unit
@echo ~CALL %pythonexe% -u %current%setup.py unittests
rem set PYTHONPATH=additional_path --> we use a virtual environment here
%pythonexe% -u %current%setup.py unittests
if %errorlevel% neq 0 exit /b %errorlevel%
@echo #######################################################6

@echo ~CALL %pythonexe% %current%setup.py clean_pyd
%pythonexe% %current%setup.py clean_pyd
pushd %current%
@echo ~CALL %pythonexe% %current%setup.py sdist --formats=gztar,zip --verbose
%pythonexe% %current%setup.py sdist --formats=gztar,zip --verbose
popd
if %errorlevel% neq 0 exit /b %errorlevel%
pushd %current%
@echo ~CALL %pythonexe% %current%setup.py bdist_wininst --plat-name=win-amd64
%pythonexe% %current%setup.py bdist_wininst --plat-name=win-amd64
popd
if %errorlevel% neq 0 exit /b %errorlevel%
pushd %current%
@echo ~CALL %pythonexe% %current%setup.py bdist_msi
%pythonexe% %current%setup.py bdist_msi
popd
if %errorlevel% neq 0 exit /b %errorlevel%
pushd %current%
@echo ~CALL %pythonexe% %current%setup.py bdist_wheel
%pythonexe% %current%setup.py bdist_wheel
popd
if %errorlevel% neq 0 exit /b %errorlevel%
@echo #######################################################7

:documentation:
@echo ~LABEL documentation
@echo ~CALL %pythonexe% -u %current%setup.py build_sphinx
%pythonexe% -u %current%setup.py build_sphinx
if %errorlevel% neq 0 exit /b %errorlevel%
@echo #######################################################8

:copyfiles:
@echo ~LABEL copyfiles
if not exist dist\\html mkdir dist\\html
@echo ~CALL xcopy /E /C /I /Y _doc\\sphinxdoc\\build\\html dist\\html
xcopy /E /C /I /Y _doc\\sphinxdoc\\build\\html dist\\html
@echo ~COPY chm
if exist _doc\\sphinxdoc\\build\\htmlhelp copy _doc\\sphinxdoc\\build\\htmlhelp\\*.chm dist\\html
@echo ~COPY pdf
if exist _doc\\sphinxdoc\\build\\latex xcopy /E /C /I /Y _doc\\sphinxdoc\\build\\latex\\*.pdf dist\\html
if %errorlevel% neq 0 exit /b %errorlevel%

:end:
""".replace("PY??", _sversion()) + copy_to_pypiserver

#################
#: build script for Windows BASE + virtual environment
#################

copy_sphinx_to_dist = """
@echo SCRIPT: copy_sphinx_to_dist
if not exist dist\\html mkdir dist\\html
@echo ~CALL xcopy /E /C /I /Y _doc\\sphinxdoc\\build\\html dist\\html
xcopy /E /C /I /Y _doc\\sphinxdoc\\build\\html dist\\html
@echo ~COPY chm
if exist _doc\\sphinxdoc\\build\\htmlhelp copy _doc\\sphinxdoc\\build\\htmlhelp\\*.chm dist\\html
@echo ~COPY pdf
if exist _doc\\sphinxdoc\\build\\latex xcopy /E /C /I /Y _doc\\sphinxdoc\\build\\latex\\*.pdf dist\\html
if %errorlevel% neq 0 exit /b %errorlevel%
"""

#################
#: notebooks
#################
windows_notebook = """
@echo off
@echo SCRIPT: windows_notebook
if "%1"=="" goto default_value:
if "%1"=="default" goto default_value:
set pythonexe=%1
goto nextn:

:default_value:
@echo ~LABEL default_value
set pythonexe=__PY??_X64__
@echo ~SET pythonexe=__PY??_X64__

:nextn:
@echo ~LABEL nextn
set current=%~dp0

set current=%~dp0
if EXIST %current%setup.py goto current_is_setup:
set current=%current%..\\
cd ..
if EXIST %current%setup.py goto current_is_setup:
@echo Unable to find %current%setup.py
exit /b 1

:current_is_setup:
@echo ~SET current=%current%

set path=%path%;%pythonexe%;%pythonexe%\\Scripts
@echo ~SET path=%path%;%pythonexe%;%pythonexe%\\Scripts
@echo ~CALL jupyter-notebook --notebook-dir=_doc\\notebooks
set PYTHONPATH=%PYTHONPATH%;%current%\\src__ADDITIONAL_LOCAL_PATH__;%current%__ADDITIONAL_LOCAL_PATH__
@echo ~SET PYTHONPATH=%PYTHONPATH%;%current%\\src__ADDITIONAL_LOCAL_PATH__;%current%__ADDITIONAL_LOCAL_PATH__
@echo on
jupyter-notebook --notebook-dir=_doc\\notebooks --NotebookApp.token= --NotebookApp.password=
""".replace("PY??", _sversion())

#################
#: publish a module
#################
windows_publish = """
@echo SCRIPT: windows_publish
%pythonexe% %current%setup.py rotate --match=.whl --keep=10
rem %pythonexe% %current%setup.py sdist register
pushd %current%
%pythonexe% %current%setup.py bdist_wheel sdist --formats=gztar
%pythonexe% -m twine %current%/dist upload *.whl
%pythonexe% -m twine %current%/dist upload *.gz
set /P NVERSION=< version.txt
git tag v%NVERSION%
git push origin v%NVERSION%
popd
"""

#################
#: publish the documentation
#################
windows_publish_doc = """
@echo SCRIPT: windows_publish_doc
pushd %current%
%pythonexe% -u %current%setup.py upload_docs --upload-dir=dist/html
popd
"""

#################
#: run a pypi server
#################
windows_pypi = """
@echo SCRIPT: windows_pypi
set pythonexe=__PY??_X64__
@echo ~SET pythonexe=__PY??_X64__

if "%2"=="" goto default_port:
if "%2"=="default" goto default_port:
set portpy=%2
@echo ~SET portpy=%2
goto run:

:default_port:
@echo ~LABEL default_port
set portpy=__PORT__
@echo ~SET portpy=__PORT__

:run:
@echo ~LABEL run
@echo ~CALL %pythonexe%\\Scripts\\pypi-server.exe -v -u -p %portpy% --disable-fallback ..\\..\\local_pypi\\local_pypi_server
%pythonexe%\\Scripts\\pypi-server.exe -v -u -p %portpy% --disable-fallback ..\\..\\local_pypi\\local_pypi_server
""".replace("PY??", _sversion())

#################
#: script for Jenkins
#################
windows_jenkins = "@echo SCRIPT: windows_jenkins\nset jenkinspythonexe=__PYTHON__\n@echo ~SET jenkinspythonexe=__PYTHON__\n" + \
    "\n__PACTHPQb__\n" + \
    jenkins_windows_setup + " build_script\n" + \
    "\n__PACTHPQe__\n" + \
    windows_error + "\nauto_unittest_setup_help.bat %jenkinspythonexe% __SUFFIX__\n" + \
    windows_error

windows_jenkins_any = "@echo SCRIPT: windows_jenkins_any\nset jenkinspythonexe=__PYTHON__\n@echo ~SET jenkinspythonexe=__PYTHON__\n" + \
    "\n__PACTHPQb__\n" + \
    jenkins_windows_setup + " build_script\n" + \
    "\n__PACTHPQe__\n" + \
    windows_error + "\nauto_cmd_any_setup_command.bat %jenkinspythonexe% __SUFFIX__ __COMMAND__\n" + \
    windows_error

####################
#: script for Jenkins 27
####################

_second_part = """
@echo SCRIPT: _second_part
:requirements:
@echo ~LABEL requirements
@echo #######################################################_auto_setup_dep.py
cd build\\auto_setup
set pythonexe_rel=..\\..\\%jenkinspythonexe%.exe
@echo ~SET pythonexe_rel=..\\..\\%jenkinspythonexe%.exe
if exist %pythonexe_rel% goto auto_setup_relpath:
set pythonexe_rel=%jenkinspythonexe%
@echo ~SET pythonexe_rel=%jenkinspythonexe%

:auto_setup_relpath:
@echo ~LABEL auto_setup_relpath
@echo ~CALL %pythonexe_rel% auto_setup_dep.py install
%pythonexe_rel% auto_setup_dep.py install
if %errorlevel% neq 0 exit /b %errorlevel%
cd ..\\..
if %errorlevel% neq 0 exit /b %errorlevel%

@echo #######################################################_requirements_begin
echo ~SET %jenkinspythonpip%
"""

windows_jenkins_unittest27_conda = ("""
@echo off
set CURRENT_PATH=%WORKSPACE%
@echo ~SET CURRENT_PATH=%WORKSPACE%
set ROOT_VIRTUAL_ENV=%CURRENT_PATH%\\_virtualenv27
set virtual_env_py=%ROOT_VIRTUAL_ENV%\\__MODULE__
@echo ~SET virtual_env_py=%ROOT_VIRTUAL_ENV%\\__MODULE__
if exist %virtual_env_py%_conda27vir rmdir /Q /S %virtual_env_py%_conda27vir
@echo ~CALL %jenkinspythonexe%\\..\\Scripts\\conda create -p %virtual_env_py%_conda27vir --clone %jenkinspythonexe%\\.. --offline
%jenkinspythonexe%\\..\\Scripts\\conda create -p %virtual_env_py%_conda27vir --clone %jenkinspythonexe%\\.. --offline
if %errorlevel% neq 0 exit /b %errorlevel%
set jenkinspythonexe=%virtual_env_py%_conda27vir\\python
@echo ~SET jenkinspythonexe=%virtual_env_py%_conda27vir\\python
set jenkinspythonpip=%virtual_env_py%_conda27vir\\Scripts\\pip
@echo ~SET jenkinspythonpip=%virtual_env_py%_conda27vir\\Scripts\\pip
""" + _second_part).replace("PY??", _sversion())

windows_jenkins_unittest27_def_header = """
set CURRENT_PATH=%WORKSPACE%
@echo ~SET CURRENT_PATH=%WORKSPACE%
set ROOT_VIRTUAL_ENV=%CURRENT_PATH%\\_virtualenv27
@echo set ROOT_VIRTUAL_ENV=%CURRENT_PATH%\\_virtualenv27
if not exist %ROOT_VIRTUAL_ENV% mkdir %ROOT_VIRTUAL_ENV%
set virtual_env_py=%ROOT_VIRTUAL_ENV%\\__MODULE__
@echo ~SET virtual_env_py=%ROOT_VIRTUAL_ENV%\\__MODULE__
"""

windows_jenkins_unittest27_def = (windows_jenkins_unittest27_def_header + """
if exist %virtual_env_py%_vir%virtual_env_suffix% rmdir /Q /S %virtual_env_py%_vir%virtual_env_suffix%
mkdir %virtual_env_py%_vir%virtual_env_suffix%

if exist %virtual_env_py%_vir%virtual_env_suffix%\\python goto with_virtual:
set KEEPPATH=%PATH%
@echo ~SET KEEPPATH=%PATH%
set PATH=%jenkinspythonexe%\\..;%PATH%
@echo ~SET PATH=%jenkinspythonexe%\\..;%PATH%
@echo ~CALL %jenkinspythonexe%\\..\\Scripts\\virtualenv --system-site-packages %virtual_env_py%_vir%virtual_env_suffix%
%jenkinspythonexe%\\..\\Scripts\\virtualenv --system-site-packages %virtual_env_py%_vir%virtual_env_suffix%
@echo ### VIRTUAL ENVIRONMENT CREATED in %virtual_env_py%_vir%virtual_env_suffix%

@echo on
rem _PATH_VIRTUAL_ENV_
@echo off

:with_virtual:
@echo ~LABEL with_virtual
set jenkinspythonexe=%virtual_env_py%_vir%virtual_env_suffix%\\Scripts\\python
@echo ~SET jenkinspythonexe=%virtual_env_py%_vir%virtual_env_suffix%\\Scripts\\python
set jenkinspythonpip=%virtual_env_py%_vir%virtual_env_suffix%\\Scripts\\pip
@echo ~SET jenkinspythonpip=%virtual_env_py%_vir%virtual_env_suffix%\\Scripts\\pip
""" + _second_part).replace("PY??", _sversion())

windows_jenkins_27_conda = [
    "set jenkinspythonexe=__DEFAULTPYTHON__\n@echo ~SET jenkinspythonexe=__DEFAULTPYTHON__\n"
    + "\n__PACTHPQb__\n"
    + jenkins_windows_setup + " build_script\n"
    + windows_error
    + "\n@echo ~CALL %jenkinspythonexe% %current%setup.py setup_hook\n%jenkinspythonexe% %current%setup.py setup_hook\n"
    + windows_error
    + "\nauto_setup_co + y27.bat %jenkinspythonexe%\n" + windows_error,
    # next script #
    "\n__PACTHPQe__\n" +
    "set jenkinspythonexe=__PYTHON27__\n@echo ~SET jenkinspythonexe=__PYTHON27__\n" +
    windows_jenkins_unittest27_conda +
    "\n\n__REQUIREMENTS__\n\n%jenkinspythonpip% freeze\n" +
    "\nauto_cmd_run27.bat %jenkinspythonexe%\n" + windows_error,
    # next script #
    "set jenkinspythonexe=__PYTHON27__\n@echo ~SET jenkinspythonexe=__PYTHON27__\n" +
    "set CURRENT_PATH=%WORKSPACE%\n@echo ~SET CURRENT_PATH=%WORKSPACE%\n" +
    "set ROOT_VIRTUAL_ENV=%CURRENT_PATH%\\_virtualenv27\n" +
    "set virtual_env_py=%ROOT_VIRTUAL_ENV%\\__MODULE__\n@echo ~SET virtual_env_py=%ROOT_VIRTUAL_ENV%\\__MODULE__\n" +
    "set jenkinspythonexe=%virtual_env_py%_conda27vir\\python\n@echo + ~SET jenkinspythonexe=%virtual_env_py%_conda27vir\\python\n"
    "\nauto_cmd_build27.bat %jenkinspythonexe%\n" + windows_error,
    # next script #
    "copy dist_module27\\dist\\*.whl ..\\..\\local_pypi\\local_pypi_server"]

windows_jenkins_27_def = [
    "set jenkinspythonexe=__DEFAULTPYTHON__\n@echo ~SET jenkinspythonexe=__DEFAULTPYTHON__\n" +
    "\n__PACTHPQb__\n" +
    jenkins_windows_setup + " build_script\n" +
    windows_error +
    "\n@echo ~CALL %jenkinspythonexe% %current%setup.py setup_hook\n%jenkinspythonexe% %current%setup.py setup_hook\n" +
    windows_error +
    "\nauto_setup_copy27.bat %jenkinspythonexe%\n" +
    windows_error,
    # next script #
    "\n__PACTHPQe__\n" +
    "set localpythonexe=__PYTHON27__\n@echo ~SET jenkinspythonexe=__PYTHON27__\n" +
    "set jenkinspythonexe=__PYTHON27__\n@echo ~SET jenkinspythonexe=__PYTHON27__\n" +
    windows_jenkins_unittest27_def +
    "\n\n__REQUIREMENTS__\n\n" +
    "\n@echo if NOT EXIST %jenkinspythonexe%\\..\\nosetests.exe %jenkinspythonpip% install nose --upgrade --force\n" +
    "\nif NOT EXIST %jenkinspythonexe%\\..\\nosetests.exe %jenkinspythonpip% install nose --upgrade --force\n" +
    "\n@echo auto_cmd_run27.bat %jenkinspythonexe%\n\n@echo END RU +  27: %jenkinspythnexe%\n\n" +
    "\nauto_cmd_run27.bat %jenkinspythonexe%\n" + windows_error,
    # next script #
    windows_jenkins_unittest27_def_header +
    "set jenkinspythonexe=%virtual_env_py%_vir%virtual_env_suffix%\\Scripts\\python\n" +
    "@echo ~SET jenkinspythonexe=%virtual_env_py%_vir%virtual_env_su + fix%\\Scripts\\python\n" +
    "\nauto_cmd_build27.bat %jenkinspythonexe%\n" + windows_error,
    # next script #
    "copy dist_module27\\dist\\*.whl ..\\..\\local_pypi\\local_pypi_server"]

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

if "Anaconda" not in sys.version or sys.version_info[0] == 2:
    jup = ["IPython>=5.0.0", "jupyter"]
else:
    jup = []

setup(
    name=project_var_name,
    version=versionPython,
    install_requires=[
        "autopep8",
        "codecov",
        "docutils",
        "matplotlib>=1.5.1",
        "numpy>=1.11.1",
        "sphinx>=1.4.5",
        "pandas>=0.18.1",
        "python-dateutil"] + jup,
)
"""
#########################
#: copy27
#########################

copy_dist_to_local_pypi = """

set current=%~dp0
if EXIST %current%setup.py goto current_is_setup:
set current=%current%..\\
cd ..
if EXIST %current%setup.py goto current_is_setup:
@echo Unable to find %current%setup.py
exit /b 1

:current_is_setup:
@echo ~SET current=%current%

@echo SCRIPT: copy_dist_to_local_pypi
if not exist ..\\..\\local_pypi mkdir ..\\..\\local_pypi
if not exist ..\\..\\local_pypi\\local_pypi_server mkdir ..\\..\\local_pypi\\local_pypi_server
copy /Y dist\\*.whl ..\\..\\local_pypi\\local_pypi_server
"""

###############
#: blog post
###############
windows_blogpost = """
@echo SCRIPT: windows_blogpost
%pythonexe% auto_rss_server.py
"""

#####################
#: documentation server
#####################
windows_docserver = """
@echo SCRIPT: windows_docserver
%pythonexe% auto_doc_server.py
"""

########
#: pyproj
########

pyproj_template = """
<?xml version="1.0" encoding="utf-8"?>
<Project DefaultTargets="Build" xmlns="http://schemas.microsoft.com/developer/msbuild/2003" ToolsVersion="4.0">
  <PropertyGroup>
    <Configuration Condition=" '$(Configuration)' == '' ">Debug</Configuration>
    <SchemaVersion>2.0</SchemaVersion>
    <ProjectGuid>__GUID__</ProjectGuid>
    <ProjectHome>.</ProjectHome>
    <SearchPath>
    </SearchPath>
    <WorkingDirectory>.</WorkingDirectory>
    <OutputPath>.</OutputPath>
    <Name>__NAME__</Name>
    <RootNamespace>__NAME__</RootNamespace>
  </PropertyGroup>
  <PropertyGroup Condition=" '$(Configuration)' == 'Debug' ">
    <DebugSymbols>true</DebugSymbols>
    <EnableUnmanagedDebugging>false</EnableUnmanagedDebugging>
  </PropertyGroup>
  <PropertyGroup Condition=" '$(Configuration)' == 'Release' ">
    <DebugSymbols>true</DebugSymbols>
    <EnableUnmanagedDebugging>false</EnableUnmanagedDebugging>
  </PropertyGroup>
  <ItemGroup>
__INCLUDEFILES__
  </ItemGroup>
  <ItemGroup>
__INCLUDEFOLDERS__
  </ItemGroup>
  <PropertyGroup>
    <VisualStudioVersion Condition="'$(VisualStudioVersion)' == ''">10.0</VisualStudioVersion>
    <PtvsTargetsFile>$(MSBuildExtensionsPath32)\\Microsoft\\VisualStudio\\v$(VisualStudioVersion)\\Python Tools\\Microsoft.PythonTools.targets</PtvsTargetsFile>
  </PropertyGroup>
  <Import Condition="Exists($(PtvsTargetsFile))" Project="$(PtvsTargetsFile)" />
  <Import Condition="!Exists($(PtvsTargetsFile))" Project="$(MSBuildToolsPath)\\Microsoft.Common.targets" />
  <!-- Uncomment the CoreCompile target to enable the Build command in
       Visual Studio and specify your pre- and post-build commands in
       the BeforeBuild and AfterBuild targets below. -->
  <!--<Target Name="CoreCompile" />-->
  <Target Name="BeforeBuild">
  </Target>
  <Target Name="AfterBuild">
  </Target>
</Project>
"""
