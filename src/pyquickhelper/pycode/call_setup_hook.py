"""
@file
@brief  Helper for the setup.
"""
import os
import sys
import shlex
import subprocess
from ..loghelper import noLOG, run_cmd
from ..loghelper.run_cmd import get_interpreter_path
from .open_script_file import open_script


def call_setup_hook_cmd(folder, module_name, function_name="_setup_hook",
                        additional_paths=None, interpreter_path=None,
                        check=True, **args):
    """
    Prepares the command line to call function
    @see fn _setup_hook for a specific module.

    @param      folder              folder which contains the setup
    @param      module_name         module name
    @param      function_name       function to call by default
    @param      additional_paths    additional_paths to add to *sys.path* before call the function
    @param      args                additional parameter (dictionary)
    @param      interpreter_path    to use a different interpreter than the current one
    @param      check               check existence of filename
    @return                         stdout, stderr

    The function expects to find file ``__init__.py`` in
    ``<folder>/src/<module_name>``.

    .. versionadded:: 1.9
        Parameter *check* was added.
    """
    this = os.path.abspath(os.path.dirname(__file__))
    this = os.path.normpath(os.path.join(this, "..", ".."))
    src = os.path.abspath(os.path.join(folder, "src"))
    if check and not os.path.exists(src):
        src = os.path.abspath(folder)
    if check and not os.path.exists(src):
        raise FileNotFoundError(  # pragma: no cover
            "Unable to find folder '{}'.".format(folder))
    if additional_paths is None:
        additional_paths = [src, this]
    else:
        additional_paths = [src, this] + additional_paths

    if args is None or len(args) == 0:
        str_args = ""
    else:
        typstr = str
        str_args = "**" + typstr(args)

    code = ["import sys", ]
    code.extend(["sys.path.append('{0}')".format(
        d.replace("\\", "/")) for d in additional_paths])
    code.extend(["from {0} import {1}".format(module_name, function_name),
                 "{0}({1})".format(function_name, str_args),
                 "sys.exit(0)"])
    code = ";".join(code)

    if interpreter_path is None:
        interpreter_path = get_interpreter_path()

    cmd = [interpreter_path, "-c", '"{0}"'.format(code)]
    cmd = " ".join(cmd)
    return cmd, code


def call_setup_hook(folder, module_name, fLOG=noLOG, must_be=False,
                    function_name="_setup_hook", use_print=False,
                    force_call=False, additional_paths=None,
                    **args):
    """
    Calls function @see fn _setup_hook for a specific module,
    it is called in a separate process.

    @param      folder              folder which contains the setup
    @param      module_name         module name
    @param      fLOG                logging function
    @param      must_be             raises an exception if @see fn _setup_hook is not found
    @param      function_name       function to call by default
    @param      use_print           use print to display information
    @param      force_call          use *subprocess.call* instead of @see fn run_cmd
    @param      additional_paths    additional_paths to add to *sys.path* before call the function
    @param      args                additional parameter (dictionary)
    @return                         stdout, stderr

    The function expects to find file ``__init__.py`` in
    ``<folder>/src/<module_name>``.
    """
    cmd, code = call_setup_hook_cmd(folder=folder, module_name=module_name,
                                    function_name=function_name,
                                    additional_paths=additional_paths, **args)
    if use_print:  # pragma: no cover
        print("CODE:\n", code)
        print("CMD:\n", cmd)

    fLOG("[call_setup_hook] calls _setup_hook from", module_name)
    if not force_call and sys.platform.startswith("win"):
        out, err = run_cmd(  # pragma: no cover
            cmd, wait=True, fLOG=fLOG, log_error=False)
        exit = 0  # pragma: no cover
    else:
        if use_print:  # pragma: no cover
            print("subprocess.call", cmd)
        if not sys.platform.startswith("win"):
            args = shlex.split(cmd)
        else:
            args = cmd  # pragma: no cover
        exit = subprocess.call(args)
        out = "linux"
        err = ""

        if exit != 0:
            src = os.path.abspath(os.path.join(folder, "src"))
            if not os.path.exists(src):  # pragma: no cover
                src = os.path.abspath(folder)
            if not os.path.exists(src):
                raise FileNotFoundError(  # pragma: no cover
                    "Unable to find folder '{}'.".format(folder))
            init = os.path.join(src, module_name, "__init__.py")
            with open_script(init, "r") as f:
                content = f.read()
            sdef = 'def {0}'.format(function_name)
            if sdef not in content:
                exit = 0
                err = "ImportError: cannot import name '{0}'".format(
                    function_name)
    fLOG("[call_setup_hook] end of call _setup_hook")

    if use_print:  # pragma: no cover
        print("OUT:\n", out)
        if err:
            if "cannot import name '_setup_hook'" in err:
                fLOG("[call_setup_hook] _setup_hook was not found.")
            else:
                print("[pyqerror]\n", err)

    def error():
        mes = ("**CMD:\n{3}\n**CODE:\n{0}\n**OUT:\n{1}\n**[pyqerror]"
               "\n{2}\nexit={4}").format(  # pragma: no cover
            code.replace(";", "\n"), out, err, cmd, exit)
        return mes  # pragma: no cover

    if not must_be and (
        "ImportError: cannot import name '{0}'".format(function_name) in err or
            "ImportError: cannot import name {0}".format(function_name) in err):
        # no _setup_hook
        return out, "no {0}".format(function_name)
    if "Error while finding spec " in err:
        raise Exception(error())  # pragma: no cover
    if "ImportError: No module named" in err:
        raise Exception(error())  # pragma: no cover
    if exit != 0:
        raise Exception(error())  # pragma: no cover
    out = "CMD: {0}\n---\n{1}".format(cmd, out)
    return out, err
