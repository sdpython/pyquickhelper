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
    A custom exception to detect a specific location when
    *ImportError* happens in the process.
    """
    pass


class HelpGenConvertError(Exception):

    """
    Exception raised when a conversion failed.
    """
    pass


class NotebookConvertError(Exception):

    """
    Exception raised when a conversion failed.
    """
    pass
