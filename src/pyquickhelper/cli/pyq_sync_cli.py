"""
@file
@brief Wrapper function @see fn synchronize_folder into a command line.
"""
from __future__ import print_function
import os
import sys
import warnings


def pyq_sync(fLOG=print, args=None):
    """
    Synchronizes a folder using function @see fn synchronize_folder.

    @param      fLOG        logging function
    @param      args        to overwrite ``sys.args``

    .. cmdref::
        :title: Synchronize two folders
        :cmd: pyquickhelper.cli.pyq_sync_cli:pyq_sync

        Synchronizes two folders from the command line.
    """
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", ImportWarning)
        try:
            from pyquickhelper.filehelper.synchelper import synchronize_folder
            from pyquickhelper.cli.cli_helper import call_cli_function
        except ImportError:  # pragma: no cover
            folder = os.path.normpath(os.path.join(
                os.path.abspath(os.path.dirname(__file__)), "..", ".."))
            sys.path.append(folder)
            from pyquickhelper.filehelper.synchelper import synchronize_folder
            from pyquickhelper.cli.cli_helper import call_cli_function

    call_cli_function(synchronize_folder, args=args, fLOG=fLOG,
                      skip_parameters=('fLOG', 'operations', 'log1'))


if __name__ == "__main__":
    pyq_sync()  # pragma: no cover
