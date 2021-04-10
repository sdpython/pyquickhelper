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
    Returns a string showing the call stack
    when this function is called.

    .. exref::
        :title: Display the call stack

        .. runpython::
            :showcode:

            from pyquickhelper.pycode import get_call_stack
            print(get_call_stack())
    """
    s = StringIO()
    traceback.print_stack(file=s)
    return s.getvalue()
