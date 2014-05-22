"""
Documentation for this file.
"""

def check( log = False):
    """
    Checks the library is working.
    It raises an exception.
    If you want to disable the logs:
    
    @param      log     if True, display information, otherwise
    @return             0 or exception
    """
    return True
    
from .loghelper.flog import fLOG, run_cmd, unzip
from .funcwin.frame_params import open_window_params
from .funcwin.frame_function import open_window_function
from .funcwin.main_window import main_loop_functions
from .loghelper.convert_helper import str_to_datetime