# -*- coding: utf-8 -*-
"""
Main files, contains the version, the url to the documention.
"""

__version__ = "1.3"
__author__ = "Xavier Dupré"
__github__ = "https://github.com/sdpython/pyquickhelper"
__url__ = "http://www.xavierdupre.fr/app/pyquickhelper/helpsphinx/index.html"
__downloadUrl__ = "http://www.xavierdupre.fr/site2013/index_code.html#pyquickhelper"
__license__ = "MIT License"
__blog__ = """
<?xml version="1.0" encoding="UTF-8"?>
<opml version="1.0">
    <head>
        <title>blog</title>
    </head>
    <body>
        <outline text="pyquickhelper"
            title="pyquickhelper"
            type="rss"
            xmlUrl="http://www.xavierdupre.fr/app/pyquickhelper/helpsphinx/_downloads/rss.xml"
            htmlUrl="http://www.xavierdupre.fr/app/pyquickhelper/helpsphinx/blog/main_0000.html" />
    </body>
</opml>
"""


def check():
    """
    Checks the library is working.
    It raises an exception if it does not.

    @return         boolean
    """
    from .funcwin import check_icon
    from .loghelper import check_log
    check_icon()
    check_log()
    return True


def _setup_hook(add_print=False, unit_test=False):
    """
    if this function is added to the module,
    the help automation and unit tests call it first before
    anything goes on as an initialization step.
    It should be run in a separate process.

    @param      add_print       print *Success: _setup_hook*
    @param      unit_test       used only for unit testing purpose
    """
    # we can check many things, needed module
    # any others things before unit tests are started
    if add_print:
        print("Success: _setup_hook")


from .loghelper.flog import fLOG, run_cmd, skip_run_cmd, unzip, noLOG, removedirs, unzip_files
from .loghelper.url_helper import get_url_content
from .loghelper.convert_helper import str_to_datetime
from .loghelper.repositories.gitlab_helper import GitLabAPI, GitLabException
from .funcwin.frame_params import open_window_params
from .funcwin.frame_function import open_window_function
from .funcwin.main_window import main_loop_functions
from .pandashelper.readh import read_url
from .pandashelper.tblformat import df2rst, df2html
from .pandashelper.tblfunction import isempty, isnan
from .helpgen import get_help_usage
from .helpgen.sphinx_main import generate_help_sphinx, process_notebooks
from .helpgen.convert_doc_helper import docstring2html
from .helpgen.process_notebook_api import nb2slides, nb2html
from .helpgen.utils_sphinx_config import NbImage
from .serverdoc.documentation_server import run_doc_server
from .filehelper.visual_sync import create_visual_diff_through_html, create_visual_diff_through_html_files
from .filehelper.synchelper import explore_folder, synchronize_folder, has_been_updated, remove_folder
from .filehelper.synchelper import explore_folder_iterfile, explore_folder_iterfile_repo
from .filehelper.internet_helper import download
from .filehelper.compression_helper import zip_files, gzip_files, zip7_files
from .filehelper.files_status import FilesStatus
from .filehelper.ftp_transfer import TransferFTP
from .filehelper.ftp_transfer_files import FolderTransferFTP
from .filehelper.file_tree_node import FileTreeNode
from .filehelper.anyfhelper import change_file_status
from .texthelper.diacritic_helper import remove_diacritics
from .pycode.utils_tests import get_temp_folder, main_wrapper_tests
from .pycode.code_helper import remove_extra_spaces_and_pep8, remove_extra_spaces_folder
from .pycode.clean_helper import clean_exts
from .pycode.py3to2 import py3to2_convert_tree, py3to2_convert
from .pycode.setup_helper import write_version_for_setup, clean_space_for_setup, standard_help_for_setup, main_wrapper_tests, process_standard_options_for_setup
from .pycode.setup_helper import write_module_scripts


def load_ipython_extension(ip):
    """
    to allow the call ``%load_ext pyquickhelper``

    @param      ip      from ``get_ipython()``
    """
    from .ipythonhelper.magic_class_example import register_file_magics as freg
    freg(ip)
    from .ipythonhelper.magic_class_compress import register_file_magics as creg
    creg(ip)
    from .ipythonhelper.magic_class_diff import register_file_magics as dreg
    dreg(ip)
    from .ipythonhelper.magic_class_crypt import register_file_magics as ereg
    ereg(ip)
