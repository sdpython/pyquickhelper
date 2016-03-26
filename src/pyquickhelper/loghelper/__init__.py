"""
@file
@brief Shortcuts to loghelper functions
"""
from .flog import run_cmd, fLOG, noLOG, PQHException, download, unzip_files, unzip, decode_outerr, run_script, removedirs
from .convert_helper import str2datetime, timestamp_to_datetime
from .url_helper import get_url_content
from .pyrepo_helper import SourceRepository


def check_log():
    """
    check function noLOG
    """
    noLOG("try", 5, param=6)
