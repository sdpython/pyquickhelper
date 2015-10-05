"""
@file
@brief Exception raised by the automated documentation

"""


class HelpGenException(Exception):

    """
    custom exception
    """

    def __init__(self, message, file=None):
        """
        redefines the message sent to an exception

        @param      message     message
        @param      file        filename
        """
        if file is None:
            Exception.__init__(self, message)
        else:
            mes = '{0}\n  File "{1}", line 1'.format(message, file)
            Exception.__init__(self, mes)


class ImportErrorHelpGen(ImportError):

    """
    a custom exception to detect a specific location when
    *ImportError* happens in the process

    .. versionadded:: 1.0
    """
    pass


class HelpGenConvertError(Exception):

    """
    exception raised when a conversion failed

    .. versionadded:: 1.2
    """
    pass


class NotebookConvertError(Exception):

    """
    exception raised when a conversion failed

    .. versionadded:: 1.3
    """
    pass
