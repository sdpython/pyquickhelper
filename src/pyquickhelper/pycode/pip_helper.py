"""
@file
@brief Various function aruond pip

Some links to look:

* `installing_python_packages_programatically.py <https://gist.github.com/rwilcox/755524>`_
* `Calling pip programmatically <http://blog.ducky.io/python/2013/08/22/calling-pip-programmatically/>`_
"""

import os
import sys
from pip import get_installed_distributions

from ..loghelper import run_cmd, noLOG


class PQPipError (Exception):

    """
    any exception raised by one of the following function
    """

    def __init__(self, *l):
        """
        constructor

        @param      l   either a string 3 strings (cmd, out, err)
        """
        if len(l) == 1:
            Exception.__init__(self, l[0])
        else:
            cmd, out, err = l
            mes = "CMD:\n{0}\nOUT:\n{1}\nERR:\n{2}".format(cmd, out, err)
            Exception.__init__(self, mes)


def get_pip(exe_path=None):
    """
    return the name of pip to use in a command line, it also
    considers virtual environnement

    @param      exe_path        path to the executable
    @return                     path to pip
    """
    if exe_path is None:
        exe = os.path.dirname(sys.executable)
    else:
        exe = exe_path

    if sys.platform.startswith("win"):
        if not exe.endswith("Scripts"):
            pi = os.path.join(exe, "Scripts", "pip.exe")
            if not os.path.exists(pi):
                # Anaconda is different
                pi = os.path.join(exe, "Scripts", "pip.exe")
                if not os.path.exists(pi):
                    raise FileNotFoundError(pi)
        else:
            pi = os.path.join(exe, "pip.exe")
            if not os.path.exists(pi):
                # Anaconda is different
                pi = os.path.join(exe, "pip.exe")
                if not os.path.exists(pi):
                    raise FileNotFoundError(pi)
    else:
        pi = os.path.join(exe, "pip")

    return pi


def get_packages_list():
    """
    calls ``pip list`` to retrieve the list of packages

    Example of package::

        'activate',
        'as_requirement',
        'check_version_conflict',
        'clone',
        'egg_name',
        'extras',
        'from_filename',
        'from_location',
        'has_version',
        'hashcmp',
        'insert_on',
        'key',
        'load_entry_point',
        'location',
        'parsed_version',
        'platform',
        'precedence',
        'project_name',
        'py_version',
        'requires',
        'version'
    """
    return get_installed_distributions(local_only=True)


def package2dict(pkg):
    """
    extract information from a package

    @param      pkg     type *pip._vendor.pkg_resources.Distribution*
    @return             dictionary
    """
    return dict(
        version=pkg.version,
        project_name=pkg.project_name,
        py_version=pkg.py_version,
        requires=pkg.requires,
        platform=pkg.platform,
        extras=pkg.extras,
        location=pkg.location)


def get_package_info(name=None, fLOG=noLOG, start=0, end=-1, _pip=None):
    """
    calls ``pip show`` to retrieve information about packages

    @param      name        name of he packages or None to get all of them in a list
    @param      fLOG        logging function
    @param      start       start at package n (in list return by @see fn get_packages_list)
    @param      end         end at package n, -1 for all
    @param      _pip        internal
    @return                 dictionary or list of dictionaries
    """
    if name is None:
        pip = _pip if _pip is not None else get_pip()
        res = []
        packs = get_packages_list()
        if end == -1:
            end = len(packs)
        nb = end - start
        if nb <= 0:
            raise PQPipError("list will be empty, unexpected, pip={0}\nstart={1}, end={2}, total={3}".format(
                pip, start, end, len(packs)))
        for i, cp in enumerate(packs[start:end]):
            pack, v = cp.project_name, cp.version
            fLOG("{0}/{1}".format(i, nb), pack, v)
            info = get_package_info(pack, _pip=pip)
            res.append(info)
        if len(res) == 0:
            raise PQPipError(
                "empty list, unexpected, pip={0}\nstart={1}, end={2}".format(pip, start, end))
        return res
    else:
        pip = _pip if _pip is not None else get_pip()
        cmd = pip + " show " + name
        out, err = run_cmd(
            cmd, wait=True, do_not_log=True, encoding="utf8", log_error=False, fLOG=None)
        if len(err) > 0:
            if "UnicodeEncodeError: 'charmap' codec can't encode character" not in err:
                raise PQPipError(cmd, out, err)
            elif "You should consider upgrading via the" in err:
                error = None
            else:
                error = err
        else:
            error = None
        lines = out.split("\n")
        res = {}
        for line in lines:
            if "Entry-Ppints:" in line:
                break
            r = line.split(":")
            if len(r) == 2:
                name, value = r
                res[name.strip()] = value.strip("\n\r ")
        if error is not None:
            res["error"] = error
        return res
