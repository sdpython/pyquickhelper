# -*- coding: utf-8 -*-
"""
Documentation for this file.
"""

__version__ = "0.5"
__author__ = "Xavier Dupré"
__github__ = "https://github.com/sdpython/pyquickhelper"
__url__ = "http://www.xavierdupre.fr/app/pyquickhelper/helpsphinx/index.html"
__downloadUrl__ = "http://www.xavierdupre.fr/site2013/index_code.html#pyquickhelper"
__license__ = "BSD License"

def check( log = False):
    """
    Checks the library is working.
    It raises an exception.
    If you want to disable the logs:
    
    @param      log     if True, display information, otherwise
    @return             0 or exception
    """
    return True
    
from .loghelper.flog import fLOG, run_cmd, unzip, noLOG
from .loghelper.url_helper import get_url_content
from .funcwin.frame_params import open_window_params
from .funcwin.frame_function import open_window_function
from .funcwin.main_window import main_loop_functions
from .loghelper.convert_helper import str_to_datetime
from .sync.synchelper import explore_folder
from .pandashelper.readh import read_url
from .pandashelper.tblformat import df_to_rst, df_to_html
from .pandashelper.tblfunction import isempty, isnan
from .helpgen import get_help_usage
from .helpgen.sphinx_main  import generate_help_sphinx