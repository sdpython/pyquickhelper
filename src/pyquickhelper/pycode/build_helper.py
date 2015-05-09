"""
@file
@brief  Produce a build file for a module following *pyquickhelper* design.

.. versionadded:: 1.1
"""

import sys
import os
from .windows_scripts import windows_error, windows_prefix, windows_setup, windows_build, windows_notebook
from .windows_scripts import windows_publish, windows_publish_doc, windows_pypi, setup_script_dependency_py
from .windows_scripts import windows_prefix_27, windows_unittest27, copy_dist_to_local_pypi
from .windows_scripts import windows_any_setup_command


def choose_path(*paths):
    """
    returns the first path which exists in the list

    @param      paths       list of paths
    @return                 a path
    """
    for path in paths:
        if os.path.exists(path):
            return path
    raise FileNotFoundError("not path exist in: " + ", ".join(paths))

#: default values, to be replaced in the build script
default_values = {
    "windows": {
        "__PY34__": choose_path("c:\\Python34", "."),
        "__PY34_X64__": choose_path("c:\\Python34_x64", "c:\\Anaconda3", "."),
        "__PY27_X64__": choose_path("c:\\Python27_x64", "c:\\Anaconda2", "c:\\Anaconda", "."),
    },
}


def private_script_replacements(script, module, requirements, port, raise_exception=True, platform=sys.platform):
    """
    run last replacements

    @param      script          script or list of scripts
    @param      module          module name
    @param      requirements    requirements
    @param      port            port
    @param      raise_exception raise an exception if there is an error, otherwise, return None
    @param      platform        platform
    @return                     modified script
    """
    if isinstance(script, list):
        return [private_script_replacements(s, module, requirements, port, raise_exception, platform) for s in script]

    if platform.startswith("win"):
        plat = "windows"
        global default_values

        values = default_values[plat].values()
        if raise_exception and len(values) != len(set(values)):
            raise FileNotFoundError("one the paths is wrong among: " +
                                    "\n".join("{0}={1}".format(k, v) for k, v in default_values[plat].items()))

        script = script.replace("__MODULE__", module)
        for k, v in default_values[plat].items():
            script = script.replace(k, v)

        # requirements
        if requirements is not None:
            rows = []
            for r in requirements:
                r = "%pythonpip% install --no-cache-dir --index-url http://localhost:{0}/simple/ {1}".format(
                    port, r)
                rows.append(r)
            reqs = "\n".join(rows)
        else:
            reqs = ""
        script = script.replace("__REQUIREMENTS__", reqs) \
                       .replace("__PORT__", str(port)) \
                       .replace("__USERNAME__", os.environ["USERNAME"])
        return script

    else:
        if raise_exception:
            raise NotImplementedError(
                "not implemented yet for this platform %s" % sys.platform)
        else:
            return None


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


def get_extra_script_command(command, module, requirements, port=8067):
    """
    produces a script which runs the notebook, a documentation server, which
    publishes...

    @param  command         command to run (*notebook*, *publish*, *publish_doc*, *local_pypi*, *setupdep*, *run27*, *build27*, *copy_dist*)
    @param  module          module name
    @param  requirements    list of dependencies (not in your python distribution)
    @param  port            port for the local pypi_server which gives the dependencies
    @return                 scripts

    The available list of commands is given by function @see fn process_standard_options_for_setup.
    """
    script = None
    if command == "notebook":
        script = windows_notebook
    elif command == "publish":
        script = "\n".join([windows_prefix, windows_publish])
    elif command == "publish_doc":
        script = "\n".join([windows_prefix, windows_publish_doc])
    elif command == "local_pypi":
        script = "\n".join([windows_prefix, windows_pypi])
    elif command == "run27":
        script = "\n".join(
            [windows_prefix_27, windows_unittest27, windows_error])
    elif command == "build27":
        script = "\n".join([windows_prefix_27, "cd dist_module27", "rmdir /S /Q dist",
                            windows_setup.replace(
                                "exe%", "exe27%") + " bdist_wheel",
                            windows_error, "cd ..", "copy dist_module27\\dist\\*.whl dist"])
    elif command == "copy_dist":
        script = copy_dist_to_local_pypi
    elif command == "setupdep":
        script = setup_script_dependency_py
    elif command == "any_setup_command":
        script = windows_any_setup_command
    else:
        raise Exception("unable to interpret command: " + command)

    # common post-processing
    if script is None:
        raise Exception("unexpected command: " + command)
    else:
        return private_script_replacements(script, module, requirements, port)
