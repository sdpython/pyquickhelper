"""
@file
@brief  Produce a build file for a module following *pyquickhelper* design.

.. versionadded:: 1.1
"""

import sys

#: default values, to be replaced in the build script
default_values = {
    "windows": {
        "__PY34__": r"c:\Python34",
        "__PY34_X64__": r"c:\Python34_x64",
    },
}

#: stop if error
windows_error = "if %errorlevel% neq 0 exit /b %errorlevel%"

#: prefix
windows_prefix = """
echo off

if "%1"=="" goto default_value_python:
set pythonexe="%1"
goto start_script:

:default_value_python:
set pythonexe="__PY34_X64__\\python"
:start_script:
"""

windows_setup = "%pythonexe% setup.py"

#: build script for Windows
windows_build = """
echo off
IF EXIST dist del /Q dist\\*.*

if "%1"=="" goto default_value:
set pythonexe=%1
%pythonexe% setup.py write_version
goto custom_python:

:default_value:
IF NOT EXIST __PY34__ GOTO checkinstall64:

:checkinstall:
IF EXIST __PY34__vir GOTO nexta:
mkdir __PY34__vir

:nexta:
IF EXIST __PY34__vir\\install GOTO fullsetupa:
__PY34__\\Scripts\\virtualenv __PY34__vir\\install --system-site-packages
if %errorlevel% neq 0 exit /b %errorlevel%

:fullsetupa:
echo #######################################################0
__PY34__vir\\install\\Scripts\\python -u setup.py install
if %errorlevel% neq 0 exit /b %errorlevel%
echo #######################################################1


:checkinstall64:
IF EXIST __PY34_X64__vir GOTO nextb:
mkdir __PY34_X64__vir

:nextb:
IF EXIST __PY34_X64__vir\\install GOTO fullsetupb:
__PY34_X64__\\Scripts\\virtualenv __PY34_X64__vir\\install --system-site-packages
if %errorlevel% neq 0 exit /b %errorlevel%

:fullsetupb:
echo #######################################################2
__PY34_X64__vir\\install\\Scripts\\python -u setup.py install
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
if exist %virtual_env_py% GOTO folder_here:
mkdir %virtual_env_py%
:folder_here:
echo %pythonexe%\\..\\Scripts\\virtualenv --system-site-packages %virtual_env_py%
if exist %virtual_env_py%\\python goto with_virtual:
%pythonexe%\\..\\Scripts\\virtualenv --system-site-packages %virtual_env_py%
if %errorlevel% neq 0 exit /b %errorlevel%

:with_virtual:
set pythonexe=%virtual_env_py%\\Scripts\\python
set pythonpip=%virtual_env_py%\\Scripts\\python

__REQUIREMENTS__

%pythonexe% setup.py write_version
%pythonexe% -u setup.py clean_space
if %errorlevel% neq 0 exit /b %errorlevel%
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
copy dist\\*.whl ..\\local_pypi_server
"""


def private_script_replacements(script, module, requirements, port):
    """
    run last replacements

    @param      script          script
    @param      module          module name
    @param      requirements    requirements
    @param      port            port
    @return                     modified script
    """
    if sys.platform.startswith("win"):
        plat = "windows"
        global default_values
        script = script.replace("__MODULE__", module)
        for k, v in default_values[plat].items():
            script = script.replace(k, v)

        # requirements
        if requirements is not None:
            rows = []
            for r in requirements:
                r = "%pythonpip% install --extra-index-url http://localhost:{0}/simple/ {1}".format(
                    port, r)
                rows.append(r)
            reqs = "\n".join(rows)
        else:
            reqs = ""
        script = script.replace("__REQUIREMENTS__", reqs) \
                       .replace("__PORT__", str(port))
        return script

    else:
        raise NotImplementedError(
            "not implemented yet for this platform %s" % sys.platform)


def get_build_script(module, requirements=None, port=8067):
    """
    builds the build script which builds the setup, run the unit tests
    and the documentation

    @param  module          module name
    @param  requirements    list of dependencies (not in your python distribution)
    @param  port            port for the local pypi_server which gives the dependencies
    @return                 scripts
    """
    global windows_build
    if requirements is None:
        requirements = []
    return private_script_replacements(windows_build, module, requirements, port)


def get_script_command(command, module, requirements, port=8067):
    """
    produces a script which runs a command available through the setup

    @param  command         command to run
    @param  module          module name
    @param  requirements    list of dependencies (not in your python distribution)
    @param  port            port for the local pypi_server which gives the dependencies
    @return                 scripts

    The available list of commands is given by function @see fn process_standard_options_for_setup.
    """
    global windows_error, windows_prefix, windows_setup
    rows = [windows_prefix]
    rows.append(windows_setup + " " + command)
    rows.append(windows_error)
    sc = "\n".join(rows)
    return private_script_replacements(sc, module, requirements, port)


windows_notebook = """
if "%1"=="" goto default_value:
set pythonexe=%1
goto nextn:

:default_value:
set pythonexe=__PY34_X64__

:nextn:
set path=%path%;%pythonexe%;%pythonexe%\\Scripts
ipython3 notebook --notebook-dir=_doc\\notebooks --matplotlib=inline
"""

windows_publish = """
%pythonexe% setup.py rotate --match=.zip --keep=1
%pythonexe% setup.py rotate --match=.tar.gz --keep=3
rem %pythonexe% setup.py sdist register
%pythonexe% setup.py sdist --formats=gztar upload
"""

windows_publish_doc = """
%pythonexe% setup.py upload_docs --upload-dir=dist/html
"""

windows_pypi = """
set pythonexe=__PY34_X64__

:custom_python:
if "%2"=="" goto default_port:
set portpy=%2
goto run:

:default_port:
set portpy=__PORT__

:run:
echo on
%pythonexe%\Scripts\pypi-server.exe -u -p %portpy% --disable-fallback .
"""


def get_extra_script_command(command, module, requirements, port=8067):
    """
    produces a script which runs the notebook, a documentation server, which
    publishes...

    @param  command         command to run (*notebook*, *publish*, *publish_doc*, *local_pypi*)
    @param  module          module name
    @param  requirements    list of dependencies (not in your python distribution)
    @param  port            port for the local pypi_server which gives the dependencies
    @return                 scripts

    The available list of commands is given by function @see fn process_standard_options_for_setup.
    """
    global windows_notebook, windows_prefix, windows_publish, windows_publish_doc, windows_pypi

    script = None
    if command == "notebook":
        script = windows_notebook
    elif command == "publish":
        script = "\n".join([windows_prefix, windows_publish])
    elif command == "publish_doc":
        script = "\n".join([windows_prefix, windows_publish_doc])
    elif command == "local_pypi":
        script = "\n".join([windows_prefix, windows_pypi])

    if script is None:
        raise Exception("unexpected command: " + command)
    else:
        return private_script_replacements(script, module, requirements, port)
