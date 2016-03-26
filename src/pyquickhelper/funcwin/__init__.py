"""
@file
@brief shortcuts to funcwin
"""
from .frame_params import open_window_params
from .frame_function import open_window_function
from .main_window import main_loop_functions
from .patchs_windows import fix_python35_dll


def check_icon():
    """
    checks the ico was installed with the module

    @return     boolean
    """
    import os
    path = os.path.dirname(__file__)
    icon = os.path.join(path, "project_ico.ico")
    if not os.path.exists(icon):
        import sys
        if sys.version_info[0] == 2:
            raise OSError(icon)
        else:
            raise FileNotFoundError(icon)
    return True
