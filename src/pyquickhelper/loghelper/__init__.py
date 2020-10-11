"""
@file
@brief Shortcuts to loghelper functions
"""
from .buffered_flog import BufferedPrint
from .convert_helper import str2datetime, timestamp_to_datetime
from .custom_log import CustomLog
from .flog import fLOG, noLOG, fLOGFormat, PQHException, download, unzip, removedirs
from .os_helper import get_machine, get_user
from .process_helper import reap_children
from .pwd_helper import set_password, get_password
from .pypi_helper import enumerate_pypi_versions_date
from .pyrepo_helper import SourceRepository
from .repositories.pygit_helper import clone as git_clone
from .run_cmd import run_cmd, decode_outerr, run_script, RunCmdException
from .sys_helper import sys_path_append, python_path_append
from .url_helper import get_url_content


def check_log():
    """
    check function noLOG
    """
    noLOG("try", 5, param=6)
