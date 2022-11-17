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
            mes = f"CMD:\n{cmd}\nOUT:\n{out}\n[piperror]\n{err}"
            Exception.__init__(self, mes)


class Distribution:
    """
    Common interface for old and recent pip packages.
    """

    def __init__(self, dist):
        self.dist = dist

    def __getattr__(self, attr):
        if attr == 'key':
            if hasattr(self.__dict__['dist'], 'key'):
                return self.__dict__['dist'].key
            return self.__dict__['dist'].canonical_name
        if attr == 'dist':
            return self.__dict__['dist']
        if attr in {'_get_metadata', 'requires', 'PKG_INFO', 'project_name',
                    'py_version', 'platform', 'extras'}:
            if hasattr(self.__dict__['dist'], attr):
                return getattr(self.__dict__['dist'], attr)
            try:
                return getattr(self.__dict__['dist']._dist, attr)
            except AttributeError as e:
                if attr == 'project_name':
                    return getattr(self.__dict__['dist']._dist, 'name')
                raise AttributeError(
                    f"Unable to find {attr!r} in {dir(self.__dict__['dist']._dist)}.") from e
        try:
            return getattr(self.__dict__['dist'], attr)
        except AttributeError as e:
            raise AttributeError(
                f"Unable to find {attr!r} in {dir(self.__dict__['dist'])}.") from e


def get_installed_distributions(local_only=True, skip=None,
                                include_editables=True, editables_only=False,
                                user_only=False, use_cmd=False):
    """
    Directs call to function *get_installed_distributions* from :epkg:`pip`.

    Return a list of installed Distribution objects.

    :param local_only: if True (default), only return installations
        local to the current virtualenv, if in a virtualenv.
    :param skip: argument is an iterable of lower-case project names to
        ignore; defaults to ``pip.compat.stdlib_pkgs`` (if *skip* is None)
    :param editables: if False, don't report editables.
    :param editables_only: if True , only report editables.
    :param user_only: if True , only report installations in the user
        site directory.
    :param use_cmd: if True, use a different process (updated package list)
    :return: list of installed Distribution objects.
    """
    if use_cmd:
        raise NotImplementedError(  # pragma: no cover
            "use_cmd should be False.")
    if skip is None:
        try:
            from pip._internal.utils.compat import stdlib_pkgs
            skip = stdlib_pkgs
        except ImportError:  # pragma: no cover
            pass
    try:
        from pip._internal.metadata import get_default_environment
        return list(map(Distribution,
                        get_default_environment().iter_installed_distributions(
                            local_only=local_only, skip=skip,
                            include_editables=include_editables,
                            editables_only=editables_only,
                            user_only=user_only)))

    except ImportError:  # pragma: no cover
        from pip._internal.utils.misc import get_installed_distributions as getd
        return list(map(Distribution, getd(
            local_only=local_only, skip=skip,
            include_editables=include_editables,
            editables_only=editables_only,
            user_only=user_only, use_cmd=use_cmd)))


def get_packages_list():
    """
    calls ``pip list`` to retrieve the list of packages
    """
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
            f"Unexpected number of results {len(res)} for {name}")
    return res[0]
