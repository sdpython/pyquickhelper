"""
@file
@brief  Helper for the setup

.. versionadded:: 1.1
"""
import os
from ..loghelper import run_cmd, noLOG
from ..loghelper.flog import get_interpreter_path


def call_setup_hook(folder, module_name, fLOG=noLOG, must_be=False,
                    function_name="_setup_hook", use_print=False):
    """
    calls function @see fn _setup_hook for a specific module,
    it is called in a separate process

    @param      folder          folder which contains the setup
    @param      module_name     module name
    @param      fLOG            logging function
    @param      must_be         raises an exception if @see fn _setup_hook is not found
    @param      function_name   function to call by default
    @param      use_print       use print to display information
    @return                     stdout, stderr

    The function expects to find file ``__init__.py`` in
    ``<folder>/src/<module_name>``.
    """
    src = os.path.abspath(os.path.join(folder, "src"))
    code = ["import sys",
            "sys.path.append('{0}')".format(src.replace("\\", "/")),
            "from {0} import {1}".format(module_name, function_name),
            "{0}()".format(function_name)]
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
    out, err = run_cmd(cmd, wait=True, fLOG=fLOG, log_error=False)
    fLOG("~~~~~~~~~ end of call _setup_hook")
    if use_print:
        print("OUT:\n", out)
        print("ERR:\n", err)

    def error():
        mes = "**CMD:\n{3}\n**CODE:\n{0}\n**OUT:\n{1}\n**ERR:\n{2}".format(code.replace(";", "\n"),
                                                                           out, err, cmd)
        return mes

    if not must_be and "ImportError: cannot import name '{0}'".format(function_name) in err:
        # no _setup_hook
        return out, "no {0}".format(function_name)
    if "Error while finding spec " in err:
        raise Exception(error())
    if "ImportError: No module named" in err:
        raise Exception(error())
    return out, err
