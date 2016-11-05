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


def is_virtual_environment():
    """
    tells if the script is run from a virtual environment

    @return     boolean

    .. versionadded:: 1.3
    """
    return (getattr(sys, "base_exec_prefix", sys.exec_prefix) != sys.exec_prefix) or hasattr(sys, 'real_prefix')


class NotImplementedErrorFromVirtualEnvironment(NotImplementedError):
    """
    defines an exception when a function does not work
    in a virtual environment

    .. versionadded:: 1.3
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

    .. versionchanged:: 1.3
        Fix a bug (do not use ModuleInstall)
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
            return compare_module_version(num, vers)
        else:
            vers = vers + (0,) * (len(num) - len(vers))
            return compare_module_version(num, vers)


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
    exe = sys.executable.replace("w.exe", "").replace(".exe", "")
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
                                        `pymyinstall <http://www.xavierdupre.fr/app/pymyinstall/helpsphinx/index.html>`_).
    @param      fLOG                    logging function
    @param      temp_folder             temporary folder (to download module if needed), by default ``<where>/download``
    @return                             stand output

    .. faqref::
        :title: How to create a virtual environment?

        The following example creates a virtual environment.
        Packages can be added by specifying the parameter *package*.

        @code
        from pyquickhelper.pycode import create_virtual_env
        fold = "my_env"
        if not os.path.exists(fold):
            os.mkdir(fold)
        create_virtual_env(fold)
        @endcode

    The function does not work from a virtual environment.
    """
    if is_virtual_environment():
        raise NotImplementedErrorFromVirtualEnvironment()

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

    The function does not work from a virtual environment.
    """
    if is_virtual_environment():
        raise NotImplementedErrorFromVirtualEnvironment()

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
            cwd = os.getcwd()
            os.chdir(os.path.dirname(local_setup))
            script = ["-u", local_setup, "install"]
            out = run_venv_script(venv, script, fLOG=fLOG, is_cmd=True,
                                  skip_err_if="Finished processing dependencies for pymyinstall==")
            os.chdir(cwd)
            return out
        else:
            cmd = pip + " install pymyinstall"
            out, err = run_cmd(cmd, wait=True, fLOG=fLOG)
            if len(err) > 0:
                raise VirtualEnvError(
                    "unable to install pymyinstall at {2}\nCMD:\n{3}\nOUT:\n{0}\nERR:\n{1}".format(out, err, venv, cmd))
            return out
    else:
        p = os.path.normpath(os.path.join(
            os.path.abspath(os.path.dirname(__file__)), "..", ".."))
        ls = ','.join("'{0}'".format(_) for _ in packages)
        script = ["import sys",
                  "sys.path.append('{0}')".format(p.replace("\\", "\\\\")),
                  "import pymyinstall",
                  "ps=[{0}]".format(ls),
                  "t='{0}'".format(temp_folder.replace("\\", "\\\\")),
                  "pymyinstall.packaged.install_all(temp_folder=t,list_module=ps,up_pip=False)"]
        return run_venv_script(venv, "\n".join(script), fLOG=fLOG)


def run_venv_script(venv, script, fLOG=noLOG, file=False, is_cmd=False,
                    skip_err_if=None, **kwargs):
    """
    run a script on a vritual environment (the script should be simple

    @param      venv        virtual environment
    @param      script      script as a string (not a file)
    @param      fLOG        logging function
    @param      file        is script a file or a string to execute
    @param      is_cmd      if True, script is a command line to run (as a list) for python executable
    @param      skip_err_if do not pay attention to standard error if this string was found in standard output
    @param      kwargs      others arguments for function @see fn run_cmd.
    @return                 output

    The function does not work from a virtual environment.
    """
    if is_virtual_environment():
        raise NotImplementedErrorFromVirtualEnvironment()

    if sys.platform.startswith("win"):
        exe = os.path.join(venv, "Scripts", "python")
    else:
        exe = os.path.join(venv, "bin", "python")
    if is_cmd:
        cmd = " ".join([exe] + script)
        out, err = run_cmd(cmd, wait=True, fLOG=fLOG, **kwargs)
        if len(err) > 0 and (skip_err_if is None or skip_err_if not in out):
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
        out, err = run_cmd(cmd, wait=True, fLOG=fLOG, **kwargs)
        if len(err) > 0:
            raise VirtualEnvError(
                "unable to run script at {2}\nCMD:\n{3}\nOUT:\n{0}\nERR:\n{1}".format(out, err, venv, cmd))
        return out


def run_base_script(script, fLOG=noLOG, file=False, is_cmd=False,
                    skip_err_if=None, argv=None, **kwargs):
    """
    run a script with the original intepreter even if this function
    is run from a virtual environment

    @param      script      script as a string (not a file)
    @param      fLOG        logging function
    @param      file        is script a file or a string to execute
    @param      is_cmd      if True, script is a command line to run (as a list) for python executable
    @param      skip_err_if do not pay attention to standard error if this string was found in standard output
    @param      argv        list of arguments to add on the command line
    @param      kwargs      others arguments for function @see fn run_cmd.
    @return                 output

    The function does not work from a virtual environment.
    The function does not raise an exception if the standard error
    contains something like::

        ----------------------------------------------------------------------
        Ran 1 test in 0.281s

        OK


    """
    def true_err(err):
        if "Ran 1 test" in err and "OK" in err:
            return False
        else:
            return True

    if hasattr(sys, 'real_prefix'):
        exe = sys.real_prefix
    elif hasattr(sys, "base_exec_prefix"):
        exe = sys.base_exec_prefix
    else:
        exe = sys.exec_prefix
    if sys.platform.startswith("win"):
        exe = os.path.join(exe, "python")
    else:
        exe = os.path.join(exe, "bin", "python")
    if is_cmd:
        cmd = " ".join([exe] + script)
        if argv is not None:
            cmd += " " + " ".join(argv)
        out, err = run_cmd(cmd, wait=True, fLOG=fLOG, **kwargs)
        if len(err) > 0 and (skip_err_if is None or skip_err_if not in out) and true_err(err):
            p = sys.base_prefix if hasattr(sys, "base_prefix") else sys.prefix
            raise VirtualEnvError(
                "unable to run cmd at {2}\nCMD:\n{3}\nOUT:\n{0}\nERR:\n{1}".format(out, err, p, cmd))
        return out
    else:
        script = ";".join(script.split("\n"))
        if file:
            if not os.path.exists(script):
                raise FileNotFoundError(script)
            cmd = " ".join([exe, "-u", '"{0}"'.format(script)])
        else:
            cmd = " ".join([exe, "-u", "-c", '"{0}"'.format(script)])
        if argv is not None:
            cmd += " " + " ".join(argv)
        out, err = run_cmd(cmd, wait=True, fLOG=fLOG, **kwargs)
        if len(err) > 0 and true_err(err):
            p = sys.base_prefix if hasattr(sys, "base_prefix") else sys.prefix
            raise VirtualEnvError(
                "unable to run script with {2}\nCMD:\n{3}\nOUT:\n{0}\nERR:\n{1}".format(out, err, p, cmd))
        return out


def check_readme_syntax(readme, folder, version="0.8", fLOG=noLOG):
    """
    check the syntax of the file readme.rst which describes a python project

    @param      readme          file to check
    @param      folder          location for the virtual environment
    @param      version         version of docutils
    @param      fLOG            logging function
    @return                     output or SyntaxError exception

    `pipy server <https://pypi.python.org/pypi/>`_ is based on
    `docutils <https://pypi.python.org/pypi/docutils/>`_ ==0.8.
    The most simple way to check its syntax is to create a virtual environment,
    to install docutils==0.8 and to compile the file.
    This is what this function does.

    Unfortunately, this functionality does not work yet
    from a virtual environment.

    .. versionadded:: 1.3
    """
    if is_virtual_environment():
        raise NotImplementedErrorFromVirtualEnvironment()

    if not os.path.exists(folder):
        os.makedirs(folder)

    out = create_virtual_env(folder, fLOG=fLOG, packages=[
                             "docutils==" + version,
                             "pipdeptree"])
    outfile = os.path.join(folder, "conv_readme.html")

    script = ["from docutils import core",
              "import io",
              'from docutils.readers.standalone import Reader',
              'from docutils.parsers.rst import Parser',
              'from docutils.parsers.rst.directives.images import Image',
              'from docutils.parsers.rst.directives import _directives',
              'from docutils.writers.html4css1 import Writer',
              "from docutils.languages import _languages",
              "from docutils.languages import en, fr",
              "_languages['en'] = en",
              "_languages['fr'] = fr",
              "_directives['image'] = Image",
              "with open('{0}', 'r', encoding='utf8') as g: s = g.read()".format(
                  readme.replace("\\", "\\\\")),
              "settings_overrides = {'output_encoding': 'unicode', 'doctitle_xform': True, 'initial_header_level': 2, 'warning_stream': io.StringIO()}",
              "parts = core.publish_parts(source=s, parser=Parser(), reader=Reader(), source_path=None, destination_path=None, writer=Writer(),",
              "            settings_overrides=settings_overrides)",
              "with open('{0}', 'w', encoding='utf8') as f: f.write(parts['whole'])".format(
                  outfile.replace("\\", "\\\\")),
              ]

    file_script = os.path.join(folder, "test_" + os.path.split(readme)[-1])
    with open(file_script, "w") as f:
        f.write("\n".join(script))

    out = run_venv_script(folder, file_script, fLOG=fLOG, file=True)
    with open(outfile, "r", encoding="utf8") as h:
        content = h.read()

    if "System Message" in content:
        raise SyntaxError(
            "unable to parse a file with docutils==" + version + "\nCONTENT:\n" + content)

    return out
