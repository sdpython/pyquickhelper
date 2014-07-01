"""
@file
@brief Functions to help using pywin32
"""

def import_pywin32():
    """
    For the module ``pywin32``,
    this function tries to add the path to the DLL to ``PATH``
    before throwing the exception: 
    ``DLL load failed: The specified module could not be found``.
    """
    try:
        import win32com
    except ImportError as e :
        if "DLL load failed:" in str(e):
            import os,sys
            path = os.path.join(os.path.split(sys.executable)[0], "Lib","site-packages","pywin32_system32")
            os.environ["PATH"] = os.environ["PATH"] + ";" + path
            try:
                import win32com
            except ImportError as ee :
                dll = os.listdir(path)
                dll = [os.path.join(path,_) for _ in dll if "dll" in _]
                raise ImportError("some DLL must be copied:\n" + "\n".join(dll)) from e
        else :
            raise e
    
