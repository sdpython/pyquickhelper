# -*- coding: utf-8 -*-
"""
@file
@brief This file is to compare different documentation style.
"""


def f1(a, b):
    """
    Addition 1

    @param      a       parameter a
    @param      b       parameter b
    @return             ``a+b``
    """
    return a + b


def f2(a, b):
    """Addition 2
    @param      a       parameter a
    @param      b       parameter b
    @return             ``a+b``"""
    return a + b


def f3(a, b):
    """
    Addition 3

    :param a: parameter a
    :param b: parameter a
    :returns: ``a+b``
    """
    return a + b


def f4(a, b):
    """Addition 4

    :param a: parameter a
    :param b: parameter a

    :returns: ``a+b``"""
    return a + b


def f5(a, b):
    """
    Addition 5

    Parameters
    ----------

    a: parameter a

    b: parameter b

    Returns
    -------
    ``a+b``
    """
    return a + b


def f6(a, b):
    """
    Addition 6

    Args:
        a: parameter a
        b: parameter b

    Returns:
        ``a+b``
    """
    return a + b
