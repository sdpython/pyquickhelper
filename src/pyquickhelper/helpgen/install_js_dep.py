"""
@file
@brief Install javascript dependencies for the documentation generation.
"""

import os
from ..loghelper.flog import noLOG
from .install_custom import download_revealjs
from ..filehelper import synchronize_folder


def install_javascript_tools(root, dest, fLOG=noLOG,
                             revealjs_github=False):
    """
    install extra dependencies such as reveal.js

    @param      temp_folder         temporary folder
    @param      root                location of the documentation
    @param      dest                location of static path
    @param      revealjs_github     to get reveal.js from github

    The function will create sub folders in folder *root*.
    """
    # reveal.js
    if revealjs_github:
        rev = os.path.join(dest, "reveal.js")
        if not os.path.exists(rev):
            download_revealjs(root, dest, fLOG=fLOG)
        else:
            return []
    else:
        rev = os.path.join(dest, "reveal.js")
        if not os.path.exists(rev):
            try:
                import sphinxjp.themes.revealjs
            except ImportError as e:
                raise ImportError(
                    "module sphinxjp.themes.revealjs is needed to get reveal.js javascript files")

            folder = os.path.dirname(sphinxjp.themes.revealjs.__file__)
            js = os.path.join(folder, "templates", "revealjs", "static")
            os.mkdir(rev)
            sync = synchronize_folder(js, rev, copy_1to2=True)
            return [s[1].fullname for s in sync]
        else:
            return []
