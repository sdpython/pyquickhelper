"""
@file
@brief Various function to deal with pandas tables
"""


def isempty(s):
    """
    checks that a string is empty, returns also True if s is ``NaN``

    @param      s       ``str`` or ``numpy.NaN``
    @return             boolean

    The function imports :epkg:`numpy` (delayed import).
    """
    if s is None:
        return True
    if isinstance(s, str):
        return len(s) == 0

    import numpy
    if numpy.isnan(s):
        return True
    return False  # pragma: no cover


def isnan(s):
    """
    calls :epkg:`numpy:isnan` but checks it is a float first

    @param      s       object
    @return             boolean

    @raise      TypeError   if ``s`` is not a ``float``

    The function imports :epkg:`numpy` (delayed import).
    """
    if isinstance(s, float):
        import numpy
        return numpy.isnan(s)
    raise TypeError(  # pragma: no cover
        "wrong type before calling numpy.isnan: {0}".format(type(s)))
