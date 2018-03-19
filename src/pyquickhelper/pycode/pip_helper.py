"""
@file
@brief Helpers for pip

Some links to look:

* `installing_python_packages_programatically.py <https://gist.github.com/rwilcox/755524>`_
* `Calling pip programmatically <http://blog.ducky.io/python/2013/08/22/calling-pip-programmatically/>`_
"""
import sys


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
            mes = "CMD:\n{0}\nOUT:\n{1}\n[piperror]\n{2}".format(cmd, out, err)
            Exception.__init__(self, mes)


def fix_pip_902():
    """
    Version 9.0.2 of pip introduced some weird checkings in file
    `pip/_vendor/requests/packages.py <https://github.com/pypa/pip/blob/master/src/pip/_vendor/requests/packages.py>`_.
    Option 1 is to avoid that version,
    option 2 is to try to fix it.

    @return     added keys in ``sys.modules``

    See blog post
    :ref:`pip 9.0.2 and issue with pip._vendor.urllib3.contrib <blog-pip-vendor-urllib3-contrib>`,
    the following code must be run before the error
    ``KeyError: 'pip._vendor.urllib3.contrib'`` is raised.

    ::

        from pyquickhelper.pycode.pip_helper import fix_pip_902
        fix_pip_902()
    """
    keys = ['pip._vendor.urllib3.contrib',
            'pip._vendor.urllib3.contrib.pyopenssl',
            'pip._vendor.urllib3.packages.backports',
            'pip._vendor.urllib3.packages.backports.makefile',
            'pip._vendor.urllib3.contrib.socks']
    res = []
    for key in keys:
        if key not in sys.modules:
            sys.modules[key] = None
            res.append(key)
    return set(res)


def get_packages_list():
    """
    calls ``pip list`` to retrieve the list of packages
    """
    from pip import get_installed_distributions
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


def get_package_info(name=None, start=0, end=-1):
    """
    calls ``pip show`` to retrieve information about packages

    @param      name        name of he packages or None to get all of them in a list
    @param      start       start at package n (in list return by @see fn get_packages_list)
    @param      end         end at package n, -1 for all
    @return                 dictionary or list of dictionaries
    """
    from pip.commands.show import search_packages_info
    if name is None:
        res = []
        packs = get_packages_list()
        if end == -1:
            end = len(packs)
        subp = packs[start:end]
        if len(subp) == 0:
            raise PQPipError(
                "no package, start={0}, end={1}, len(subp)={2}, len(packs)={3}".format(start, end, len(subp), len(packs)))
        for i, cp in enumerate(subp):
            pack = cp.project_name
            info = get_package_info(pack)
            res.append(info)
        if len(res) == 0 and len(subp) > 0:
            raise PQPipError(
                "empty list, unexpected, start={0}, end={1}, len(subp)={3}".format(start, end, len(subp)))
        return res
    else:
        res = [_ for _ in search_packages_info([name])]
        if len(res) != 1:
            raise PQPipError(
                "unexpected number of results {0} for {1}".format(len(res), name))
        return res[0]
