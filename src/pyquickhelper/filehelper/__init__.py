"""
Various checking
"""
import os


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


from .synchelper import explore_folder, synchronize_folder, has_been_updated, remove_folder
from .synchelper import explore_folder_iterfile, explore_folder_iterfile_repo
from .visual_sync import create_visual_diff_through_html, create_visual_diff_through_html_files
from .compression_helper import zip_files, gzip_files, zip7_files
from .file_tree_node import FileTreeNode
from .anyfhelper import change_file_status
