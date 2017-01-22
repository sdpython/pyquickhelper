"""
@file
@brief Shortcuts to loghelper functions
"""
from .custom_log import CustomLog
from .flog import fLOG, noLOG, PQHException, download, unzip, removedirs
from .convert_helper import str2datetime, timestamp_to_datetime
from .run_cmd import run_cmd, decode_outerr, run_script, RunCmdException
from .url_helper import get_url_content
from .pyrepo_helper import SourceRepository
from .repositories.pygit_helper import clone as git_clone


def check_log():
    """
    check function noLOG
    """
    noLOG("try", 5, param=6)
