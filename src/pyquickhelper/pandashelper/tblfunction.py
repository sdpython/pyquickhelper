"""
@file
@brief Various function to deal with pandas tables
"""


def isempty(s):
    """
    checks that a string is empty, returns also True if s is ``NaN``

    @param      s       ``str`` or ``numpy.NaN``
    @return             boolean

    .. versionchanged:: 1.3
        We import numpy in the function (delayed import).
    """
    if s is None:
        return True
    if isinstance(s, str  # unicode#
                  ):
        return len(s) == 0

    import numpy
    if numpy.isnan(s):
        return True
    return False


def isnan(s):
    """
    calls :epkg:`numpy:isnan` but checks it is a float first

    @param      s       object
    @return             boolean

    @raise      TypeError   if ``s`` is not a ``float``

    .. versionchanged:: 1.3
        We import numpy in the function (delayed import).
    """
    if isinstance(s, float):
        import numpy
        return numpy.isnan(s)
    else:
        raise TypeError(
            "wrong type before calling numpy.isnan: {0}".format(type(s)))
