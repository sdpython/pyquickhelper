# -*- coding: utf-8 -*-
"""
@file
@brief Implements command line ``python -m pyquickhelper <command> <args>``.

.. versionadded:: 1.8
"""
import sys


def main(args, fLOG=print):
    """
    Implements ``python -m pyquickhelper <command> <args>``.

    @param      args        command line arguments
    @param      fLOG        logging function
    """
    try:
        from .cli.pyq_sync_cli import pyq_sync
        from .cli.encryption_file_cli import encrypt_file, decrypt_file
        from .cli.encryption_cli import encrypt, decrypt
        from .pandashelper import df2rst
        from .pycode import clean_files
        from .cli import cli_main_helper
        from .helpgen import process_notebooks
        from .filehelper import create_visual_diff_through_html_files
        from .filehelper import explore_folder
    except ImportError:
        from pyquickhelper.cli.pyq_sync_cli import pyq_sync
        from pyquickhelper.cli.encryption_file_cli import encrypt_file, decrypt_file
        from pyquickhelper.cli.encryption_cli import encrypt, decrypt
        from pyquickhelper.pandashelper import df2rst
        from pyquickhelper.pycode import clean_files
        from pyquickhelper.cli import cli_main_helper
        from pyquickhelper.helpgen import process_notebooks
        from pyquickhelper.filehelper import create_visual_diff_through_html_files
        from pyquickhelper.filehelper import explore_folder

    fcts = dict(synchronize_folder=pyq_sync, encrypt_file=encrypt_file,
                decrypt_file=decrypt_file, encrypt=encrypt,
                decrypt=decrypt, df2rst=df2rst, clean_files=clean_files,
                process_notebooks=process_notebooks,
                visual_diff=create_visual_diff_through_html_files,
                ls=explore_folder)
    return cli_main_helper(fcts, args=args, fLOG=fLOG)


if __name__ == "__main__":
    main(sys.argv[1:])
