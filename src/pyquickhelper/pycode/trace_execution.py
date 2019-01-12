"""
@brief
@file Various function to help investigate an error.
"""
import traceback
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
