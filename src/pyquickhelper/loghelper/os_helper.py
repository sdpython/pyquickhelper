"""
@file
@brief Helpers for OS

.. versionadded:: 1.5
"""
import os


def get_machine():
    """
    Returns the machine name.

    @return     machine name
    """
    name = os.environ.get("COMPUTERNAME",
                          os.environ.get("HOSTNAME",
                                         os.environ.get("NAME",
                                                        os.environ.get("TRAVIS_OS_NAME", None))))
    if name is None:
        raise ValueError("Unable to find machine name in {0}".format(
            ",".join(sorted(os.environ.keys()))))
    return name


def get_user():
    """
    Returns the user name.

    @return     user name
    """
    name = os.environ.get("USERNAME", os.environ.get("USER", None))
    if name is None:
        raise ValueError("Unable to find user name in {0}".format(
            ",".join(sorted(os.environ.keys()))))
    return name
