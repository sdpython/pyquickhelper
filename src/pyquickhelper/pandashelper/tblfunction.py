"""
@file
@brief Various function to deal with pandas tables
"""

import numpy

def isempty(s):
    """
    checks that a string is empty, returns also True if s is ``NaN``
    
    @param      s       ``str`` or ``numpy.NaN``
    @return             boolean
    """
    if isinstance (s, str): return len(s) == 0
    if numpy.isnan(s) : return True
    return False
    
def isnan(s):
    """
    calls `numpy.isnan <http://docs.scipy.org/doc/numpy/reference/generated/numpy.isnan.html>`_ but checks it is a float first
    
    @param      s       object
    @return             boolean
    
    @raise      TypeError   if ``s`` is not a ``float``
    """
    if isinstance(s,float):
        return numpy.isnan(s)
    else :
        raise TypeError("wrong type before calling numpy.isnan: {0}".format(type(s)))
    