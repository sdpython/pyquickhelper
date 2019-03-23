"""
@file
@brief Install javascript dependencies for the documentation generation.
"""

import os
from ..loghelper.flog import noLOG
from .install_custom import download_revealjs, download_requirejs
from ..filehelper import synchronize_folder, change_file_status


def install_javascript_tools(root, dest, fLOG=noLOG,
                             revealjs_github=False):
    """
    Installs extra dependencies such as :epkg:`reveal.js`.

    @param      root                location of the documentation
    @param      dest                location of static path
    @param      fLOG                logging function
    @param      revealjs_github     to get :epkg:`reveal.js` from github

    The function will create sub folders in folder *root*.
    """
    # delayed import to speed up time
    from ..sphinxext import revealjs

    # reveal.js
    if revealjs_github:
        rev = os.path.join(dest, "reveal.js")
        if not os.path.exists(rev):
            lfiles = download_revealjs(root, dest, fLOG=fLOG)
        else:
            lfiles = []
    else:
        rev = os.path.join(dest, "reveal.js")
        if not os.path.exists(rev):

            folder = os.path.dirname(revealjs.__file__)
            js = os.path.join(folder, "templates", "revealjs", "static")
            os.mkdir(rev)
            sync = synchronize_folder(js, rev, copy_1to2=True, fLOG=fLOG)
            fulls = [s[1].fullname for s in sync]
            change_file_status(rev)
            lfiles = fulls
        else:
            lfiles = []

    # require.js
    expected = os.path.join(dest, "require.js")
    if not os.path.exists(expected):
        one = download_requirejs(dest, fLOG=fLOG)
    else:
        one = [expected]
    lfiles.extend(one)
    return lfiles
