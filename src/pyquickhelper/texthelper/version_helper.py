# -*- coding: utf-8 -*-
"""
@file
@brief Helpers about versionning.

.. versionadded:: 1.8
"""


def numeric_module_version(vers):
    """
    Converts a string into a tuple with numbers wherever possible.

    @param      vers    string
    @return             tuple
    """
    if isinstance(vers, tuple):
        return vers
    spl = vers.split(".")
    r = []
    for _ in spl:
        try:
            i = int(_)
            r.append(i)
        except ValueError:
            r.append(_)
    return tuple(r)


def compare_module_version(num, vers):
    """
    Compares two versions.

    @param      num     first version
    @param      vers    second version
    @return             -1, 0, 1

    This function implements something similar to
    *StrictVersion* (from *distutils*) but
    probably more simple.
    """
    if num is None:
        if vers is None:
            return 0
        else:
            return 1
    if vers is None:
        return -1

    if not isinstance(vers, tuple):
        vers = numeric_module_version(vers)
    if not isinstance(num, tuple):
        num = numeric_module_version(num)

    if len(num) == len(vers):
        for a, b in zip(num, vers):
            if isinstance(a, int) and isinstance(b, int):
                if a < b:
                    return -1
                elif a > b:
                    return 1
            else:
                a = str(a)
                b = str(b)
                if a < b:
                    return -1
                if a > b:
                    return 1  # pragma: no cover
        return 0
    if len(num) < len(vers):
        num = num + (0,) * (len(vers) - len(num))
        return compare_module_version(num, vers)
    vers = vers + (0,) * (len(num) - len(vers))
    return compare_module_version(num, vers)
