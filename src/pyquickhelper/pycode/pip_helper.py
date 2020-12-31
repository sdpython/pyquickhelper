"""
@file
@brief Helpers for pip

Some links to look:

* `installing_python_packages_programatically.py <https://gist.github.com/rwilcox/755524>`_
* `Calling pip programmatically <http://blog.ducky.io/python/2013/08/22/calling-pip-programmatically/>`_
"""


class PQPipError(Exception):
    """
    Any exception raised by one of the following function.
    """

    def __init__(self, *args):
        """
        @param      args    either a string 3 strings (cmd, out, err)
        """
        if len(args) == 1:
            Exception.__init__(self, args[0])  # pragma: no cover
        else:
            cmd, out, err = args
            mes = "CMD:\n{0}\nOUT:\n{1}\n[piperror]\n{2}".format(cmd, out, err)
            Exception.__init__(self, mes)


def get_packages_list():
    """
    calls ``pip list`` to retrieve the list of packages
    """
    from pip._internal.utils.misc import get_installed_distributions
    return get_installed_distributions(local_only=True)


def package2dict(pkg):
    """
    Extracts information from a package.

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
    Calls ``pip show`` to retrieve information about packages.

    @param      name        name of he packages or None to get all of them in a list
    @param      start       start at package n (in list return by @see fn get_packages_list)
    @param      end         end at package n, -1 for all
    @return                 dictionary or list of dictionaries
    """
    from pip._internal.commands.show import search_packages_info
    if name is None:
        res = []
        packs = get_packages_list()
        if end == -1:
            end = len(packs)  # pragma: no cover
        subp = packs[start:end]
        if len(subp) == 0:
            raise PQPipError(  # pragma: no cover
                "No package, start={0}, end={1}, len(subp)={2}, len(packs)={3}".format(
                    start, end, len(subp), len(packs)))
        for cp in subp:
            pack = cp.project_name
            info = get_package_info(pack)
            res.append(info)
        if len(res) == 0 and len(subp) > 0:
            raise PQPipError(  # pragma: no cover
                "Empty list, unexpected, start={0}, end={1}, len(subp)={3}".format(
                    start, end, len(subp)))
        return res

    res = list(search_packages_info([name]))
    if len(res) != 1:
        raise PQPipError(  # pragma: no cover
            "Unexpected number of results {0} for {1}".format(
                len(res), name))
    return res[0]
