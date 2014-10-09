"""
@file
@brief 
"""

def check_icon():
    """
    checks the ico was installed with the module
    
    @return     boolean
    """
    import os
    path = os.path.dirname(__file__)
    icon = os.path.join(path, "project_ico.ico")
    if not os.path.exists(icon):
        raise FileNotFoundError(icon)
    return True
    