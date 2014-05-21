#-*- coding: utf-8 -*-
"""
@file
@brief Various functions about conversions.
"""
import datetime

def str_to_datetime (dt, format = None):
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
    """
    if "+" in dt : dt = dt.split("+")[0].strip()
    elif " -" in dt : dt = dt.split(" -")[0].strip()
    if format == None :
        if "." in dt :        
            return datetime.datetime.strptime (dt, "%Y-%m-%d %H:%M:%S.%f")    
        else :
            return datetime.datetime.strptime (dt, "%Y-%m-%d %H:%M:%S")
    else :
        return datetime.datetime.strptime (dt, format)

def timestamp_to_datetime(timestamp):
    """
    convert a time into a datetime
    @param      ctime       ctime object (time)
    @rtype                  datetime
    """
    return datetime.datetime.utcfromtimestamp(timestamp)
    