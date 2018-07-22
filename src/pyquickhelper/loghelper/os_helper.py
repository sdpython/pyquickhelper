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
