"""
@file
@brief Helpers for virtualenv
"""
import os
import sys


class VirtualEnvError(Exception):
    """
    Exception raised by the function implemented in this file.
    """
    pass


def is_virtual_environment():
    """
    Tells if the script is run from a virtual environment.

    @return     boolean
    """
    return (getattr(sys, "base_exec_prefix", sys.exec_prefix) != sys.exec_prefix) or hasattr(sys, 'real_prefix')


class NotImplementedErrorFromVirtualEnvironment(NotImplementedError):
    """
    Defines an exception when a function does not work
    in a virtual environment.
    """
    pass


def build_venv_cmd(params, posparams):  # pragma: no cover
    """
    Builds the command line for virtual env.

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


def create_virtual_env(where, symlinks=False,
                       system_site_packages=False,
                       clear=True, packages=None, fLOG=None,
                       temp_folder=None, platform=None):  # pragma: no cover
    """
    Creates a virtual environment.

    @param      where                   location of this virtual environment
    @param      symlinks                attempt to symlink rather than copy
    @param      system_site_packages    Give the virtual environment access to the system site-packages dir
    @param      clear                   Delete the environment directory if it already exists.
                                        If not specified and the directory exists, an error is raised.
    @param      packages                list of packages to install (it will install module
                                        :epkg:`pymyinstall`).
    @param      fLOG                    logging function
    @param      temp_folder             temporary folder (to download module if needed), by default ``<where>/download``
    @param      platform                platform to use
    @return                             stand output

    .. index:: virtual environment

    .. faqref::
        :title: How to create a virtual environment?

        The following example creates a virtual environment.
        Packages can be added by specifying the parameter *package*.

        ::

            from pyquickhelper.pycode import create_virtual_env
            fold = "my_env"
            if not os.path.exists(fold):
                os.mkdir(fold)
            create_virtual_env(fold)

    The function does not work from a virtual environment.
    """
    from ..loghelper import run_cmd
    if fLOG is None:
        from ..loghelper import noLOG
        fLOG = noLOG
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
            "unable to create virtual environement at {2}\nCMD:\n{3}\nOUT:\n{0}\n[pyqerror]\n{1}".format(out, err, where, cmd))

    if platform is None:
        platform = sys.platform
    if platform.startswith("win"):
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
                            temp_folder=temp_folder,
                            platform=platform)
    in_scripts = os.listdir(scripts)
    pips = [_ for _ in in_scripts if _.startswith("pip")]
    if len(pips) == 0:
        raise FileNotFoundError(
            "unable to find pip in {0}, content:\n  {1}".format(scripts, in_scripts))

    out += venv_install(where, "pymyinstall", fLOG=fLOG,
                        temp_folder=temp_folder, platform=platform)

    if packages is not None and len(packages) > 0:
        fLOG("install packages in:", where)
        packages = [_ for _ in packages if _ not in ("pymyinstall", "pip")]
        if len(packages) > 0:
            out += venv_install(where, packages, fLOG=fLOG,
                                temp_folder=temp_folder,
                                platform=platform)
    return out


def venv_install(venv, packages, fLOG=None,
                 temp_folder=None, platform=None):  # pragma: no cover
    """
    Installs a package or a list of packages in a virtual environment.

    @param      venv            location of the virtual environment
    @param      packages        a package (str) or a list of packages(list[str])
    @param      fLOG            logging function
    @param      temp_folder     temporary folder (to download module if needed), by default ``<where>/download``
    @param      platform        platform (``sys.platform`` by default)
    @return                     standard output

    The function does not work from a virtual environment.
    """
    from ..loghelper import run_cmd
    if fLOG is None:
        from ..loghelper import noLOG
        fLOG = noLOG
    if is_virtual_environment():
        raise NotImplementedErrorFromVirtualEnvironment()
    if temp_folder is None:
        temp_folder = os.path.join(venv, "download")
    if isinstance(packages, str):
        packages = [packages]
    if platform is None:
        platform = sys.platform

    if packages == "pip" or packages == ["pip"]:  # pylint: disable=R1714
        from .get_pip import __file__ as pip_loc  # pylint: disable=E0401
        ppath = os.path.abspath(pip_loc.replace(".pyc", ".py"))
        script = ["-u", ppath]
        return run_venv_script(venv, script, fLOG=fLOG, is_cmd=True, platform=platform)
    elif packages == "pymyinstall" or packages == ["pymyinstall"]:  # pylint: disable=R1714
        if platform.startswith("win"):
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
                                  skip_err_if="Finished processing dependencies for pymyinstall==",
                                  platform=platform)
            os.chdir(cwd)
            return out
        else:
            cmd = pip + " install pymyinstall"
            out, err = run_cmd(cmd, wait=True, fLOG=fLOG)
            if len(err) > 0:
                raise VirtualEnvError(
                    "unable to install pymyinstall at {2}\nCMD:\n{3}\nOUT:\n{0}\n[pyqerror]\n{1}".format(out, err, venv, cmd))
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
        return run_venv_script(venv, "\n".join(script), fLOG=fLOG, platform=platform)


def run_venv_script(venv, script, fLOG=None,
                    file=False, is_cmd=False,
                    skip_err_if=None, platform=None,
                    **kwargs):  # pragma: no cover
    """
    Runs a script on a vritual environment (the script should be simple).

    @param      venv        virtual environment
    @param      script      script as a string (not a file)
    @param      fLOG        logging function
    @param      file        is script a file or a string to execute
    @param      is_cmd      if True, script is a command line to run (as a list) for python executable
    @param      skip_err_if do not pay attention to standard error if this string was found in standard output
    @param      platform    platform (``sys.platform`` by default)
    @param      kwargs      others arguments for function @see fn run_cmd.
    @return                 output

    The function does not work from a virtual environment.
    """
    from ..loghelper import run_cmd
    if fLOG is None:
        from ..loghelper import noLOG
        fLOG = noLOG

    def filter_err(err):
        lis = err.split("\n")
        lines = []
        for li in lis:
            if "missing dependencies" in li:
                continue
            if "' misses '" in li:
                continue
            lines.append(li)
        return "\n".join(lines).strip(" \r\n\t")

    if is_virtual_environment():
        raise NotImplementedErrorFromVirtualEnvironment()

    if platform is None:
        platform = sys.platform

    if platform.startswith("win"):
        exe = os.path.join(venv, "Scripts", "python")
    else:
        exe = os.path.join(venv, "bin", "python")
    if is_cmd:
        cmd = " ".join([exe] + script)
        out, err = run_cmd(cmd, wait=True, fLOG=fLOG, **kwargs)
        err = filter_err(err)
        if len(err) > 0 and (skip_err_if is None or skip_err_if not in out):
            raise VirtualEnvError(
                "unable to run cmd at {2}\n--CMD--\n{3}\n--OUT--\n{0}\n[pyqerror]"
                "\n{1}".format(out, err, venv, cmd))
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
        err = filter_err(err)
        if len(err) > 0:
            raise VirtualEnvError(
                "Unable to run script at {2}\n--CMD--\n{3}\n--OUT--\n{0}\n"
                "[pyqerror]\n{1}".format(out, err, venv, cmd))
        return out


def run_base_script(script, fLOG=None, file=False, is_cmd=False,
                    skip_err_if=None, argv=None, platform=None, **kwargs):
    """
    Runs a script with the original intepreter even if this function
    is run from a virtual environment.

    @param      script      script as a string (not a file)
    @param      fLOG        logging function
    @param      file        is script a file or a string to execute
    @param      is_cmd      if True, script is a command line to run (as a list) for python executable
    @param      skip_err_if do not pay attention to standard error if this string was found in standard output
    @param      argv        list of arguments to add on the command line
    @param      platform    platform (``sys.platform`` by default)
    @param      kwargs      others arguments for function @see fn run_cmd.
    @return                 output

    The function does not work from a virtual environment.
    The function does not raise an exception if the standard error
    contains something like::

        ----------------------------------------------------------------------
        Ran 1 test in 0.281s

        OK
    """
    from ..loghelper import run_cmd
    if fLOG is None:  # pragma: no cover
        from ..loghelper import noLOG
        fLOG = noLOG

    def true_err(err):  # pragma: no cover
        if "Ran 1 test" in err and "OK" in err:
            return False
        return True

    if platform is None:
        platform = sys.platform

    if hasattr(sys, 'real_prefix'):  # pragma: no cover
        exe = sys.base_prefix
    elif hasattr(sys, "base_exec_prefix"):  # pragma: no cover
        exe = sys.base_exec_prefix
    else:
        exe = sys.exec_prefix  # pragma: no cover

    if platform.startswith("win"):
        exe = os.path.join(exe, "python")  # pragma: no cover
    else:
        exe = os.path.join(exe, "bin", "python%d.%d" % sys.version_info[:2])
        if not os.path.exists(exe):
            exe = os.path.join(exe, "bin", "python")  # pragma: no cover

    if is_cmd:  # pragma: no cover
        cmd = " ".join([exe] + script)
        if argv is not None:
            cmd += " " + " ".join(argv)
        out, err = run_cmd(cmd, wait=True, fLOG=fLOG, **kwargs)
        if len(err) > 0 and (skip_err_if is None or skip_err_if not in out) and true_err(err):
            p = sys.base_prefix if hasattr(sys, "base_prefix") else sys.prefix
            raise VirtualEnvError(
                "unable to run cmd at {2}\nCMD:\n{3}\nOUT:\n{0}\n[pyqerror]\n{1}".format(out, err, p, cmd))
        return out
    else:
        script = ";".join(script.split("\n"))
        if file:
            if not os.path.exists(script):
                raise FileNotFoundError(script)  # pragma: no cover
            cmd = " ".join([exe, "-u", '"{0}"'.format(script)])
        else:
            cmd = " ".join(
                [exe, "-u", "-c", '"{0}"'.format(script)])  # pragma: no cover
        if argv is not None:
            cmd += " " + " ".join(argv)  # pragma: no cover
        out, err = run_cmd(cmd, wait=True, fLOG=fLOG, **kwargs)
        if len(err) > 0 and true_err(err):
            p = (sys.base_prefix  # pragma: no cover
                 if hasattr(sys, "base_prefix")
                 else sys.prefix)
            raise VirtualEnvError(  # pragma: no cover
                "unable to run script with {2}\nCMD:\n{3}\nOUT:\n{0}\n[pyqerror]\n{1}".format(out, err, p, cmd))
        return out


def check_readme_syntax(readme, folder,
                        version="0.8", fLOG=None):  # pragma: no cover
    """
    Checks the syntax of the file ``readme.rst``
    which describes a python project.

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
    """
    if fLOG is None:
        from ..loghelper import noLOG
        fLOG = noLOG
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
              "settings_overrides = {'output_encoding': 'unicode', 'doctitle_xform': True,",
              "            'initial_header_level': 2, 'warning_stream': io.StringIO()}",
              "parts = core.publish_parts(source=s, parser=Parser(), reader=Reader(), source_path=None,",
              "            destination_path=None, writer=Writer(),",
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
