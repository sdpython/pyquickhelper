

def onefunction(a, b: int=4):
    """
    Return the addition of ``a+b``.

    :param a: first element
    :param b: second element
    :return: ``a + b``
    :raises TypeError: if a and b have different types.
    """
    if type(a) != type(b):
        raise TypeError("Different type {0} != {1}".format(a, b))
    return a + b
