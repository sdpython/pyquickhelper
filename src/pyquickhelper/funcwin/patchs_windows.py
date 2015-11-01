"""
@file
@brief Patches installation

.. versionadded:: 1.3
"""

import os
import sys
import shutil


def fix_python35_dll(path1, path2, force=False):
    """
    This function tries to adress a known issue when
    creating a virtual environment on Windows with Python 3.5

    @param      path1       Python installation
    @param      path2       virtual environment
    @param      force       force the replication even if Python version 3.5 is not true
    @return                 list of copied assemblies

    This comes from the following message::

        ERROR: It thinks sys.prefix is 'c:\\jenkins\\pymy\\py35_actuariat_python'
                (should be 'c:\\jenkins\\pymy\\py35_actuariat_python\\_virtualenv\\actuariat_python_virpy35_505506092c_505506092c')
        ERROR: virtualenv is not compatible with this system or executable
        Note: some Windows users have reported this error when they installed Python for "Only this user"
              or have multiple versions of Python installed.
              Copying the appropriate PythonXX.dll to the virtualenv Scripts/ directory may fix this problem.
    """
    if not force and sys.version_info[:2] != (3, 5):
        return []
    if os.path.isfile(path1):
        path1 = os.path.dirname(path1)
    if os.path.isfile(path2):
        path2 = os.path.dirname(path2)
    paths2s = [path2]
    path3 = os.path.join(path2, "Scripts")
    if os.path.exists(path3):
        paths2s = [path3]
    dll = os.listdir(path1)
    copy = []
    for f in dll:
        ext = os.path.splitext(f)[-1]
        if ext == ".dll":
            full = os.path.join(path1, f)
            for path2 in paths2s:
                to = os.path.join(path2, f)
                if not os.path.exists(to):
                    copy.append(to)
                    shutil.copy(full, path2)

    return copy


if __name__ == "__main__":
    arg = [_ for _ in sys.argv if ".py" not in _]
    if len(arg) != 2:
        print("Usage: {0} <path_to_python35> <virtual_env>".format(
            os.path.split(__file__)[-1]))
    else:
        fix_python35_dll(*arg)
