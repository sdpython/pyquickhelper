

class clex:
    """
    Class help.
    """

    def __init__(self):
        """
        Constructor
        """
        pass

    def onemethod(self, a, b):
        """
        Return the addition of ``a+b``.

        :param a: first element
        :param c: second element
        :return: ``a + b``
        :raises TypeError: guess
        """
        if type(a) != type(b):
            raise TypeError("Different type {0} != {1}".format(a, b))
        return a + b

    @staticmethod
    def static_method(a, b):
        """
        Return the static addition of ``a+b``.

        :param a: first element
        :param c: second element
        :return: ``a + b``
        :raises TypeError: guess
        """
        if type(a) != type(b):
            raise TypeError("Different type {0} != {1}".format(a, b))
        return a + b
