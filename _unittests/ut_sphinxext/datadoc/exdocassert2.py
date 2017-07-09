

def onefunction(a, b):
    """
    Return the addition of ``a+b``.
    Second line should be aligned.

    :param a: first element
    :param c: second element
    :return: ``a + b``
    :raises TypeError: guess
    """
    if type(a) != type(b):
        raise TypeError("Different type {0} != {1}".format(a, b))
    return a + b
