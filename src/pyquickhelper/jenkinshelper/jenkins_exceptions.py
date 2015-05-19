"""
@file
@brief Jenkins exceptions

.. versionadded:: 1.1
"""


class JenkinsExtException(Exception):

    """
    exception for the class JenkinsExt
    """
    pass


class JenkinsExtPyException(Exception):

    """
    exception for the class JenkinsExt, when a distribution is not available
    """
    pass


class JenkinsJobException(Exception):

    """
    exception for the class JenkinsExt, the job definition is wrong
    """
    pass
