# -*- coding: utf-8 -*-
"""
@file
@brief logged exception

By default, all exceptions are logged through the function fLOG (@see fn fLOG).

::

    raise PQHException ("message")
"""


class PQHException (Exception):

    """
    Define an exception.

    - exception used in Python module to make exception
      raised by this module easier to catch
    - every time exception is logged
    """

    def __init__(self, m, log=True):
        """constructor
        @param      m       message
        @param      log     log the exception
        """
        Exception.__init__(self, m)
        if log:
            from .flog import fLOG
            fLOG("PQHException", m)
