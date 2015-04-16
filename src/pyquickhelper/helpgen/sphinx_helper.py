# -*- coding: utf-8 -*-
"""
@file
@brief Various helpers for Sphinx.
"""

import os
import sys

from ..filehelper import synchronize_folder, explore_folder_iterfile
from ..loghelper.flog import noLOG

if sys.version_info[0] == 2:
    from codecs import open


def everything_but_python(fullname):
    """
    return True
    """
    if "__pycache__" in fullname:
        return False
    return os.path.splitext(fullname)[-1] not in [".py", ".pyc"]


def sphinx_add_scripts(source, dest, filter=everything_but_python):
    """
    copy additional scripts to a folder for sphinx documentation

    @param  source      source
    @param  dest        destination folder (will be created if it does not exists)
    @return             @see fn synchronize_folder
    """

    if not os.path.exists(dest):
        os.makedirs(dest)

    res = synchronize_folder(
        source, dest, repo1=False, repo2=False, filter=filter)
    return res


def post_process_html_nb_output_static_file(build, fLOG=noLOG):
    """
    post process the HTML files produced by Sphinx to adjust the static files
    in notebooks (IPython static files do have the same paths as
    Sphinx static files)

    @param      build       build location
    @return                 list of modified files

    Static path in IPython start by ``/static``, they start by ``../_static``
    or ``/_static`` in Sphinx.
    """
    if not os.path.exists(build):
        raise FileNotFoundError(build)

    tofind = ' src="/static/'
    torep = ' src="../_static/'

    res = []
    for full in explore_folder_iterfile(build, pattern=".*[.]html"):
        with open(full, "r", encoding="utf8") as f:
            content = f.read()

        if tofind in content:
            res.append(full)
            fLOG("[post_process_html_nb_output_static_file]", full)
            content = content.replace(tofind, torep)
            with open(full, "w", encoding="utf8") as f:
                f.write(content)

    return res
