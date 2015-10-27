"""
@brief
@file Various function to help investigate an error.

.. versionadded:: 1.3
"""
import sys
import traceback

if sys.version_info[0] == 2:
    from StringIO import StringIO
else:
    from io import StringIO


class ErrorOnPurpose(Exception):
    """
    raise to get the call stack
    """
    pass


def get_call_stack():
    """
    returns a string showing the call stack
    when this function is called
    
    @return                     string
    """
    s = StringIO()
    traceback.print_stack(file=s)
    return s.getvalue()
