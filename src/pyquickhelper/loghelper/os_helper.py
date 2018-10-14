"""
@file
@brief Helpers for module :epkg:`*py:os`.
"""
import os


def get_machine():
    """
    Returns the machine name.

    @return     machine name

    The method assumes environment variable ``COMPUTERNAME``,
    ``HOSTNAME`` or ``NAME`` is available.
    Otherwise, you should use module ``platform``.
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

    The method assumes environment variable ``USERNAME`` or ``USER``
    is available.
    """
    name = os.environ.get("USERNAME", os.environ.get(
        "USER", os.environ.get("CIRCLE_USERNAME", None)))
    if name is None:
        raise ValueError("Unable to find user name in {0}".format(
            ",".join(sorted(os.environ.keys()))))
    return name
