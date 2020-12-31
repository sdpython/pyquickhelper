"""
@file
@brief Functions to help using pywin32
"""


def import_pywin32():  # pragma: no cover
    """
    For the module ``pywin32``,
    this function tries to add the path to the DLL to ``PATH``
    before throwing the exception:
    ``DLL load failed: The specified module could not be found``.
    """
    try:
        import win32com
        return win32com
    except ImportError as e:
        if "DLL load failed:" in str(e):
            import os
            import sys
            import numpy
            from distutils.sysconfig import get_python_lib

            paths = set([os.path.join(
                os.path.split(sys.executable)[0], "Lib", "site-packages", "pywin32_system32"),
                os.path.join(get_python_lib(), "pywin32_system32"),
                os.path.join(
                    os.path.dirname(numpy.__file__), "..", "pywin32_system32"),
            ])

            epath = os.environ["PATH"]
            last_path = None
            for path in paths:
                last_path = path
                # exe = os.path.abspath(os.path.dirname(sys.executable))
                os.environ["PATH"] = epath + ";" + path

                try:
                    import win32com
                    return win32com
                except ImportError:
                    # we try the next path
                    continue

            try:
                import win32com
                return win32com
            except ImportError:
                # addition for WinPython
                exe = os.path.abspath(os.path.dirname(sys.executable))
                os.environ["PATH"] = os.environ["PATH"] + ";" + exe
                try:
                    import win32com
                    return win32com
                except ImportError:
                    dll = os.listdir(last_path)
                    dll = [os.path.join(last_path, _)
                           for _ in dll if "dll" in _]
                    if len(dll) == 0:
                        raise ImportError("Did you install pywin32?") from e
                    raise ImportError(
                        "Some DLL must be copied:\n" + "\n".join(dll)) from e
        else:
            raise e
