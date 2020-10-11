"""
@file
@brief Helpers to store and retrieve password.
"""


def set_password(system, username, password, lib='keyring'):
    """
    Stores a password.
    By default, uses :epkg:`keyring`.

    :param system: system
    :param username: username
    :param password: password
    :param lib: which lib to use to store the password
    """
    if lib == 'keyring':
        from keyring import (
            set_password as lib_set_password,
            get_password as lib_get_password)
        lib_set_password(system, username, password)
        pwd = lib_get_password(system, username)
        if pwd != password:
            raise RuntimeError(  # pragma: no cover
                "Unable to store a password with keyring for '{}', '{}'.".format(
                    system, username))
        return
    raise RuntimeError(
        "Unknown library '{}'.".format(lib))


def get_password(system, username, lib='keyring'):
    """
    Restores a password.
    By default, uses :epkg:`keyring`.

    :param system: system
    :param username: username
    :param lib: which lib to use to store the password
    :return: password
    """
    if lib == 'keyring':
        from keyring import get_password as lib_get_password
        pwd = lib_get_password(system, username)
        if pwd in (None, '', b''):
            raise RuntimeError(  # pragma: no cover
                "Unable to restore a password with keyring for '{}', '{}'.".format(
                    system, username))
        return pwd
    raise RuntimeError(
        "Unknown library '{}'.".format(lib))
