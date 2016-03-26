# -*- coding: utf-8 -*-
"""
@file
@brief Various functions about conversions.
"""
import datetime


def str2datetime(dt, format=None):
    """
    convert a string into a datetime object, it can be:
        - 2013-05-24 18:49:46
        - 2013-05-24 18:49:46.568

    @param      dt      string
    @param      format  format for the conversion, the most complete one is:
                            @code
                            %Y-%m-%d %H:%M:%S.%f
                            @endcode
                        which you get by default
    @rtype              datetime
    @return             datetime

    .. versionchanged:: 1.0
        accept more formats (no time, T instead of space)
    """
    if "+" in dt:
        dt = dt.split("+")[0].strip()
    elif " -" in dt:
        dt = dt.split(" -")[0].strip()
    if format is None:
        if " " in dt:
            if "." in dt:
                return datetime.datetime.strptime(dt, "%Y-%m-%d %H:%M:%S.%f")
            else:
                return datetime.datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
        elif "T" in dt:
            if "." in dt:
                return datetime.datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S.%f")
            else:
                return datetime.datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S")
        else:
            return datetime.datetime.strptime(dt, "%Y-%m-%d")
    else:
        return datetime.datetime.strptime(dt, format)


def datetime2str(dt):
    """
    convert a datetime into a string

    @param      dt      datetime
    @return             string

    .. versionadded:: 1.3
    """
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def timestamp_to_datetime(timestamp):
    """
    convert a time into a datetime
    @param      ctime       ctime object (time)
    @rtype                  datetime
    """
    return datetime.datetime.utcfromtimestamp(timestamp)
