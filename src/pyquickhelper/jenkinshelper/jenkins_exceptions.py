"""
@file
@brief Jenkins exceptions

.. versionadded:: 1.1
"""


class JenkinsExtException(Exception):
    """
    Exception for the class @see cl JenkinsExt.
    """
    pass


class JenkinsExtPyException(Exception):
    """
    Exception for the class @see cl JenkinsExt,
    when a distribution is not available.
    """
    pass


class JenkinsJobException(Exception):
    """
    Exception for the class @see cl JenkinsExt,
    the job definition is wrong.
    """
    pass
