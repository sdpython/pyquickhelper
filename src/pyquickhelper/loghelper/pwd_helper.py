"""
@file
@brief Helpers to store and retrieve password.
"""
from getpass import getpass
from os import getenv


def set_password(system, username, password, lib='keyrings.cryptfile',
                 env='KEYRING_CRYPTFILE_PASSWORD', ask=True):
    """
    Stores a password.
    By default, uses :epkg:`keyring` or
    :epkg:`keyrings.cryptfile`.

    :param system: system
    :param username: username
    :param password: password
    :param lib: which lib to use to store the password
    :param env: see below
    :param ask: ask for password if missing

    If `lib == 'keyrings.cryptfile'`, the function used the environment
    variable *env*, if present, no password is asked.
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
    if lib == 'keyrings.cryptfile':
        from keyrings.cryptfile.cryptfile import CryptFileKeyring
        kr = CryptFileKeyring()
        kr.keyring_key = getenv("KEYRING_CRYPTFILE_PASSWORD")
        if kr.keyring_key is None and ask:
            kr.keyring_key = getpass()
        kr.set_password(system, username, password)
        return
    raise RuntimeError(
        "Unknown library '{}'.".format(lib))


def get_password(system, username, lib='keyrings.cryptfile',
                 env='KEYRING_CRYPTFILE_PASSWORD', ask=True):
    """
    Restores a password.
    By default, uses :epkg:`keyring`.

    :param system: system
    :param username: username
    :param lib: which lib to use to store the password
    :param env: see below
    :param ask: ask for password if missing
    :return: password

    If `lib == 'keyrings.cryptfile'`, the function used the environment
    variable *env*, if present, no password is asked.
    """
    if lib == 'keyring':
        from keyring import get_password as lib_get_password
        pwd = lib_get_password(system, username)
        if pwd in (None, '', b''):
            raise RuntimeError(  # pragma: no cover
                "Unable to restore a password with keyring for '{}', '{}'.".format(
                    system, username))
        return pwd
    if lib == 'keyrings.cryptfile':
        from keyrings.cryptfile.cryptfile import CryptFileKeyring
        kr = CryptFileKeyring()
        kr.keyring_key = getenv("KEYRING_CRYPTFILE_PASSWORD")
        if kr.keyring_key is None and ask:
            kr.keyring_key = getpass()
        return kr.get_password(system, username)
    raise RuntimeError(
        "Unknown library '{}'.".format(lib))
