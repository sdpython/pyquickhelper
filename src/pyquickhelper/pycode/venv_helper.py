"""
@file
@brief Helpers for virtualenv

.. versionadded:: 1.2
"""
import os
import sys
from ..loghelper import noLOG, run_cmd


class VirtualEnvError(Exception):
    """
    exception raised by the function implemented in this file
    """
    pass


def numeric_module_version(vers):
    """
    convert a string into a tuple with numbers whever possible

    @param      vers    string
    @return             tuple
    """
    if isinstance(vers, tuple):
        return vers
    spl = vers.split(".")
    r = []
    for _ in spl:
        try:
            i = int(_)
            r.append(i)
        except:
            r.append(_)
    return tuple(r)


def compare_module_version(num, vers):
    """
    compare two versions

    @param      num     first version
    @param      vers    second version
    @return             -1, 0, 1
    """
    if num is None:
        if vers is None:
            return 0
        else:
            return 1
    if vers is None:
        return -1

    if not isinstance(vers, tuple):
        vers = numeric_module_version(vers)
    if not isinstance(num, tuple):
        num = numeric_module_version(num)

    if len(num) == len(vers):
        for a, b in zip(num, vers):
            if isinstance(a, int) and isinstance(b, int):
                if a < b:
                    return -1
                elif a > b:
                    return 1
            else:
                a = str(a)
                b = str(b)
                if a < b:
                    return -1
                elif a > b:
                    return 1
        return 0
    else:
        if len(num) < len(vers):
            num = num + (0,) * (len(vers) - len(num))
            return ModuleInstall.compare_version(num, vers)
        else:
            vers = vers + (0,) * (len(num) - len(vers))
            return ModuleInstall.compare_version(num, vers)


def build_venv_cmd(params, posparams):
    """
    builds the command line for virtual env

    @param      params      dictionary of parameters
    @param      posparams   positional arguments
    @return                 string
    """
    import venv
    v = venv.__file__
    if v is None:
        raise ImportError("module venv should have a version number")
    exe = sys.executable
    cmd = [exe, "-m", "venv"]
    for k, v in params.items():
        if v is None:
            cmd.append("--" + k)
        else:
            cmd.append("--" + k + "=" + v)
    cmd.extend(posparams)
    return " ".join(cmd)


def create_virtual_env(where, symlinks=False, system_site_packages=False,
                       clear=True, packages=None, fLOG=noLOG,
                       temp_folder=None):
    """
    .. index:: virtual environment

    create a virtual environment

    @param      where                   location of this virtual environment
    @param      symlinks                attempt to symlink rather than copy
    @param      system_site_packages    Give the virtual environment access to the system site-packages dir
    @param      clear                   Delete the environment directory if it already exists.
                                        If not specified and the directory exists, an error is raised.
    @param      packages                list of packages to install (it will install module
                                        `pymyinstall <>`_).
    @param      fLOG                    logging function
    @param      temp_folder             temporary folder (to download module if needed), by default ``<where>/download``
    @return                             stand output

    @example(Create a virtual environment)
    The following example creates a virtual environment.
    Packages can be added by specifying the parameter *package*.

    @code
    from pyquickhelper.pycode import create_virtual_env
    fold = "my_env"
    if not os.path.exists(fold):
        os.mkdir(fold)
    create_virtual_env(fold)
    @endcode

    @endexample
    """
    fLOG("create virtual environment at:", where)
    params = {}
    if symlinks:
        params["symlinks"] = None
    if system_site_packages:
        params["system-site-packages"] = None
    if clear:
        params["clear"] = None
    cmd = build_venv_cmd(params, [where])
    out, err = run_cmd(cmd, wait=True, fLOG=fLOG)
    if len(err) > 0:
        raise VirtualEnvError(
            "unable to create virtual environement at {2}\nCMD:\n{3}\nOUT:\n{0}\nERR:\n{1}".format(out, err, where, cmd))

    if sys.platform.startswith("win"):
        scripts = os.path.join(where, "Scripts")
    else:
        scripts = os.path.join(where, "bin")

    if not os.path.exists(scripts):
        files = "\n  ".join(os.listdir(where))
        raise FileNotFoundError(
            "unable to find {0}, content:\n  {1}".format(scripts, files))

    in_scripts = os.listdir(scripts)
    pips = [_ for _ in in_scripts if _.startswith("pip")]
    if len(pips) == 0:
        out += venv_install(where, "pip", fLOG=fLOG,
                            temp_folder=temp_folder)
    in_scripts = os.listdir(scripts)
    pips = [_ for _ in in_scripts if _.startswith("pip")]
    if len(pips) == 0:
        raise FileNotFoundError(
            "unable to find pip in {0}, content:\n  {1}".format(scripts, in_scripts))

    out += venv_install(where, "pymyinstall", fLOG=fLOG,
                        temp_folder=temp_folder)

    if packages is not None and len(packages) > 0:
        fLOG("install packages in:", where)
        packages = [_ for _ in packages if _ != "pymyinstall" and _ != "pip"]
        if len(packages) > 0:
            out += venv_install(where, packages, fLOG=fLOG,
                                temp_folder=temp_folder)
    return out


def venv_install(venv, packages, fLOG=noLOG, temp_folder=None):
    """
    install a package or a list of packages in a virtual environment

    @param      venv            location of the virtual environment
    @param      packages        a package (str) or a list of packages(list[str])
    @param      fLOG            logging function
    @param      temp_folder     temporary folder (to download module if needed), by default ``<where>/download``
    @return                     standard output
    """
    if temp_folder is None:
        temp_folder = os.path.join(venv, "download")

    if isinstance(packages, str):
        packages = [packages]

    if packages == "pip" or packages == ["pip"]:
        from .get_pip import __file__ as pip_loc
        ppath = os.path.abspath(pip_loc.replace(".pyc", ".py"))
        script = ["-u", ppath]
        return run_venv_script(venv, script, fLOG=fLOG, is_cmd=True)
    elif packages == "pymyinstall" or packages == ["pymyinstall"]:
        if sys.platform.startswith("win"):
            pip = os.path.join(venv, "Scripts", "pip")
        else:
            pip = os.path.join(venv, "bin", "pip")
        local_setup = os.path.abspath(os.path.join(os.path.dirname(
            __file__), "..", "..", "..", "..", "pymyinstall", "setup.py"))
        if os.path.exists(local_setup):
            cmd = sys.executable + " " + local_setup + " install"
            out, err = run_cmd(cmd, wait=True, fLOG=fLOG)
            if len(err) > 0:
                raise VirtualEnvError(
                    "unable to install pymyinstall at {2}\nCMD:\n{3}\nOUT:\n{0}\nERR:\n{1}".format(out, err, venv, cmd))
            return out
        else:
            stop
            cmd = pip + " install pymyinstall"
            out, err = run_cmd(cmd, wait=True, fLOG=fLOG)
            if len(err) > 0:
                raise VirtualEnvError(
                    "unable to install pymyinstall at {2}\nCMD:\n{3}\nOUT:\n{0}\nERR:\n{1}".format(out, err, venv, cmd))
            return out
    else:
        p = os.path.normpath(os.path.join(
            os.path.abspath(os.path.dirname(__file__)), "..", ".."))
        l = ','.join("'{0}'".format(_) for _ in packages)
        script = ["import sys",
                  "sys.path.append('{0}')".format(p.replace("\\", "\\\\")),
                  "import pymyinstall",
                  "ps=[{0}]".format(l),
                  "t='{0}'".format(temp_folder.replace("\\", "\\\\")),
                  "pymyinstall.packaged.install_all(temp_folder=t,list_module=ps)"]
        return run_venv_script(venv, "\n".join(script), fLOG=fLOG)


def run_venv_script(venv, script, fLOG=noLOG, file=False, is_cmd=False):
    """
    run a script on a vritual environment (the script should be simple

    @param      venv        virtual environment
    @param      script      script as a string (not a file)
    @param      fLOG        logging function
    @param      file        is script a file or a string to execute
    @param      is_cmd      if True, script is a command line to run (as a list) for python executable
    @return                 output
    """
    if sys.platform.startswith("win"):
        exe = os.path.join(venv, "Scripts", "python")
    else:
        exe = os.path.join(venv, "bin", "python")
    if is_cmd:
        cmd = " ".join([exe] + script)
        out, err = run_cmd(cmd, wait=True, fLOG=fLOG)
        if len(err) > 0:
            raise VirtualEnvError(
                "unable to run cmd at {2}\nCMD:\n{3}\nOUT:\n{0}\nERR:\n{1}".format(out, err, venv, cmd))
        return out
    else:
        script = ";".join(script.split("\n"))
        if file:
            if not os.path.exists(script):
                raise FileNotFoundError(script)
            cmd = " ".join([exe, "-u", '"{0}"'.format(script)])
        else:
            cmd = " ".join([exe, "-u", "-c", '"{0}"'.format(script)])
        out, err = run_cmd(cmd, wait=True, fLOG=fLOG)
        if len(err) > 0:
            raise VirtualEnvError(
                "unable to run script at {2}\nCMD:\n{3}\nOUT:\n{0}\nERR:\n{1}".format(out, err, venv, cmd))
        return out
