"""
@file
@brief Install javascript dependencies for the documentation generation.
"""

import os
from ..loghelper.flog import noLOG
from .install_custom import download_revealjs


def install_javascript_tools(root, dest, fLOG=noLOG):
    """
    install extra dependencies such as reveal.js

    @param      temp_folder temporary folder
    @param      root        location of the documentation
    @param      dest        location of static path

    The function will create sub folders in folder *root*.
    """
    rev = os.path.join(dest, "reveal.js")
    if not os.path.exists(rev):
        download_revealjs(root, dest, fLOG=fLOG)
