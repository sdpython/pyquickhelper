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
        from .pycode import clean_files, run_test_function
        from .cli import cli_main_helper
        from .filehelper import create_visual_diff_through_html_files, explore_folder
        from .cli.simplified_fct import sphinx_rst
        from .imghelper.img_helper import zoom_img
        from .imghelper.img_export import images2pdf
        from .cli.script_exec import repeat_script
        from .cli.ftp_cli import ftp_upload
        from .cli.notebook import run_notebook, convert_notebook
        from .loghelper import set_password
        from .filehelper.download_urls_helper import download_urls_in_folder_content
    except ImportError:  # pragma: no cover
        from pyquickhelper.cli.pyq_sync_cli import pyq_sync
        from pyquickhelper.cli.encryption_file_cli import encrypt_file, decrypt_file
        from pyquickhelper.cli.encryption_cli import encrypt, decrypt
        from pyquickhelper.pandashelper import df2rst
        from pyquickhelper.pycode import clean_files, run_test_function
        from pyquickhelper.cli import cli_main_helper
        from pyquickhelper.filehelper import create_visual_diff_through_html_files, explore_folder
        from pyquickhelper.cli.simplified_fct import sphinx_rst
        from pyquickhelper.imghelper.img_helper import zoom_img
        from pyquickhelper.imghelper.img_export import images2pdf
        from pyquickhelper.cli.script_exec import repeat_script
        from pyquickhelper.cli.ftp_cli import ftp_upload
        from pyquickhelper.cli.notebook import run_notebook, convert_notebook
        from pyquickhelper.loghelper import set_password
        from pyquickhelper.filehelper.download_urls_helper import download_urls_in_folder_content

    fcts = dict(synchronize_folder=pyq_sync, encrypt_file=encrypt_file,
                decrypt_file=decrypt_file, encrypt=encrypt,
                decrypt=decrypt, df2rst=df2rst, clean_files=clean_files,
                convert_notebook=convert_notebook,
                visual_diff=create_visual_diff_through_html_files,
                ls=explore_folder, run_test_function=run_test_function,
                sphinx_rst=sphinx_rst, run_notebook=run_notebook,
                zoom_img=zoom_img, images2pdf=images2pdf,
                repeat_script=repeat_script,
                ftp_upload=ftp_upload, set_password=set_password,
                download_urls_in_folder_content=download_urls_in_folder_content)
    return cli_main_helper(fcts, args=args, fLOG=fLOG)


if __name__ == "__main__":
    main(sys.argv[1:])  # pragma: no cover
