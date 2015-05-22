"""
@file
@brief  Helper for the setup

.. versionadded:: 1.1
"""
import os
import sys
import shlex
import subprocess
from ..loghelper import noLOG, run_cmd
from ..loghelper.flog import get_interpreter_path


def call_setup_hook(folder, module_name, fLOG=noLOG, must_be=False,
                    function_name="_setup_hook", use_print=False,
                    force_call=False):
    """
    calls function @see fn _setup_hook for a specific module,
    it is called in a separate process

    @param      folder          folder which contains the setup
    @param      module_name     module name
    @param      fLOG            logging function
    @param      must_be         raises an exception if @see fn _setup_hook is not found
    @param      function_name   function to call by default
    @param      use_print       use print to display information
    @param      force_call      use *subprocess.call* instead of @see fn run_cmd
    @return                     stdout, stderr

    The function expects to find file ``__init__.py`` in
    ``<folder>/src/<module_name>``.
    """
    src = os.path.abspath(os.path.join(folder, "src"))
    code = ["import sys",
            "sys.path.append('{0}')".format(src.replace("\\", "/")),
            "from {0} import {1}".format(module_name, function_name),
            "{0}()".format(function_name),
            "sys.exit(0)"]
    code = ";".join(code)
    if use_print:
        print("CODE:\n", code)

    cmd = [get_interpreter_path(),
           "-c",
           '"{0}"'.format(code)]
    cmd = " ".join(cmd)
    if use_print:
        print("CMD:\n", cmd)

    fLOG("~~~~~~~~~ calls _setup_hook from", module_name)
    if not force_call and sys.platform.startswith("win"):
        out, err = run_cmd(cmd, wait=True, fLOG=fLOG, log_error=False)
        exit = 0
    else:
        if use_print:
            print("subprocess.call", cmd)
        if not sys.platform.startswith("win"):
            args = shlex.split(cmd)
        else:
            args = cmd
        exit = subprocess.call(args)
        out = "linux"
        err = ""

        if exit != 0:
            init = os.path.join(src, module_name, "__init__.py")
            with open(init, "r") as f:
                content = f.read()
            if 'def {0}'.format(function_name) not in content:
                exit = 0
                err = "ImportError: cannot import name '{0}'".format(
                    function_name)
    fLOG("~~~~~~~~~ end of call _setup_hook")

    if use_print:
        print("OUT:\n", out)
        print("ERR:\n", err)

    def error():
        mes = "**CMD:\n{3}\n**CODE:\n{0}\n**OUT:\n{1}\n**ERR:\n{2}\nexit={4}".format(code.replace(";", "\n"),
                                                                                     out, err, cmd, exit)
        return mes

    if not must_be and "ImportError: cannot import name '{0}'".format(function_name) in err:
        # no _setup_hook
        return out, "no {0}".format(function_name)
    if "Error while finding spec " in err:
        raise Exception(error())
    if "ImportError: No module named" in err:
        raise Exception(error())
    if exit != 0:
        raise Exception(error())
    return out, err
