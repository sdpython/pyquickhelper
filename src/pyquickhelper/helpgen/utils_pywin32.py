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
    except ImportError as e:
        if "DLL load failed:" in str(e):
            import os
            import sys
            path = os.path.join(
                os.path.split(sys.executable)[0], "Lib", "site-packages", "pywin32_system32")
            #exe = os.path.abspath(os.path.dirname(sys.executable))
            os.environ["PATH"] = os.environ["PATH"] + ";" + path
            try:
                import win32com
            except ImportError as ee:
                # addition for WinPython
                exe = os.path.abspath(os.path.dirname(sys.executable))
                os.environ["PATH"] = os.environ["PATH"] + ";" + exe
                try:
                    import win32com
                except ImportError as ee:
                    dll = os.listdir(path)
                    dll = [os.path.join(path, _) for _ in dll if "dll" in _]
                    if len(dll) == 0:
                        raise ImportError("Did you install pywin32?") from e
                    else:
                        raise ImportError(
                            "Some DLL must be copied:\n" + "\n".join(dll)) from e
        else:
            raise e
