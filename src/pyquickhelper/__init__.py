# -*- coding: utf-8 -*-
"""
Main files, contains the version, the url to the documention.
"""

__version__ = "0.7"
__author__ = "Xavier Dupré"
__github__ = "https://github.com/sdpython/pyquickhelper"
__url__ = "http://www.xavierdupre.fr/app/pyquickhelper/helpsphinx/index.html"
__downloadUrl__ = "http://www.xavierdupre.fr/site2013/index_code.html#pyquickhelper"
__license__ = "BSD License"

def check():
    """
    Checks the library is working.
    It raises an exception if it does not.
    
    @return         boolean
    """
    from .funcwin import check_icon
    check_icon()
    return True
    
from .loghelper.flog                    import fLOG, run_cmd, unzip, noLOG
from .loghelper.url_helper              import get_url_content
from .funcwin.frame_params              import open_window_params
from .funcwin.frame_function            import open_window_function
from .funcwin.main_window               import main_loop_functions
from .loghelper.convert_helper          import str_to_datetime
from .sync.synchelper                   import explore_folder, synchronize_folder, has_been_updated
from .pandashelper.readh                import read_url
from .pandashelper.tblformat            import df_to_rst, df_to_html
from .pandashelper.tblfunction          import isempty, isnan
from .helpgen                           import get_help_usage
from .helpgen.sphinx_main               import generate_help_sphinx
from .ipythonhelper.kindofcompletion    import AutoCompletion, AutoCompletionFile
from .sync.visual_sync                  import create_visual_diff_through_html