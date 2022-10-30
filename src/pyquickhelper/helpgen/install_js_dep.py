"""
@file
@brief Install javascript dependencies for the documentation generation.
"""

import os
import shutil
from ..loghelper.flog import noLOG
from .install_custom import download_revealjs, download_requirejs
from ..filehelper import (
    synchronize_folder, change_file_status, download)
from ..filehelper.internet_helper import ReadUrlException


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
        try:
            one = download_requirejs(dest, fLOG=fLOG)
        except ReadUrlException:
            name = os.path.join(os.path.dirname(__file__), "require.js")
            shutil.copy(name, expected)
            one = [expected]
    else:
        one = [expected]
    lfiles.extend(one)

    # embed-ams.js
    expected = os.path.join(dest, "embed-amd.js")
    if not os.path.exists(expected):
        url = "https://unpkg.com/@jupyter-widgets/html-manager@0.20.0/dist/embed-amd.js"
        try:
            one = [download(url, dest, fLOG=fLOG)]
        except ReadUrlException:
            name = os.path.join(os.path.dirname(__file__), "embed-amd.js")
            shutil.copy(name, expected)
            one = [expected]
    else:
        one = [expected]
    lfiles.extend(one)
    return lfiles
