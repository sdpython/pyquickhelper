"""
@file
@brief Shortcuts to filehelper
"""
import os
from .anyfhelper import change_file_status, read_content_ufs
from .compression_helper import (
    zip_files, gzip_files, zip7_files, unzip_files, ungzip_files,
    un7zip_files, unrar_files, untar_files)
from .download_helper import (
    get_url_content_timeout, get_urls_content_timeout,
    InternetException, local_url)
from .encrypted_backup import EncryptedBackup
from .encryption import decrypt_stream, encrypt_stream
from .file_info import FileInfo, is_file_string, checksum_md5, is_url_string
from .ftp_transfer import TransferFTP
from .ftp_transfer_files import FolderTransferFTP
from .file_tree_node import FileTreeNode
from .internet_helper import download, read_url
from .synchelper import explore_folder, synchronize_folder, has_been_updated, remove_folder
from .synchelper import explore_folder_iterfile, explore_folder_iterfile_repo, walk
from .transfer_api import TransferAPI
from .transfer_api_ftp import TransferAPIFtp
from .transfer_api_file import TransferAPIFile
from .visual_sync import create_visual_diff_through_html, create_visual_diff_through_html_files


def check():
    """
    checks difflibjs is present
    """
    path = os.path.abspath(os.path.dirname(__file__))
    fold = os.path.join(path, "temp_difflibjs")
    r = os.path.exists(fold)
    if not r:
        return r
    f = os.path.join(fold, "jsdifflib.zip")
    r = os.path.exists(f)
    if not r:
        return r
    size = os.stat(f).st_size
    return size > 0
