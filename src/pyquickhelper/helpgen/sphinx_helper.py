# -*- coding: utf-8 -*-
"""
@file
@brief Various helpers for Sphinx.
"""
import os
from ..filehelper import synchronize_folder, explore_folder_iterfile
from ..loghelper.flog import noLOG, fLOG


def everything_but_python(fullname):
    """
    Returns True if ``__pycache__`` is not in filename.
    """
    if "__pycache__" in fullname:
        return False
    return os.path.splitext(fullname)[-1] not in [".py", ".pyc"]


def sphinx_add_scripts(source, dest, filter=everything_but_python, fLOG=fLOG):
    """
    copy additional scripts to a folder for sphinx documentation

    @param  source      source
    @param  dest        destination folder (will be created if it does not exists)
    @param  filter      @see fn synchronize_folder
    @param  fLOG        logging function
    @return             @see fn synchronize_folder
    """

    if not os.path.exists(dest):
        os.makedirs(dest)

    res = synchronize_folder(
        source, dest, repo1=False, repo2=False, filter=filter, fLOG=fLOG)
    return res


def post_process_html_nb_output_static_file(build, fLOG=noLOG):
    """
    post process the HTML files produced by Sphinx to adjust the static files
    in notebooks (IPython static files do have the same paths as
    Sphinx static files)

    @param      build       build location
    @param      fLOG        logging function
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
        modif = False
        with open(full, "r", encoding="utf8") as f:
            try:
                content = f.read()
            except UnicodeDecodeError as e:
                # maybe it is Windows and the encoding is sometimes different
                with open(full, "r", encoding="cp1252") as g:
                    try:
                        content = g.read()
                        content = content.replace(
                            "charset=cp1252", "charset=utf-8")
                    except UnicodeDecodeError:
                        raise FileNotFoundError(
                            "Unable to load %r\n%r" % (full, os.path.abspath(full))) from e

        if tofind in content:
            res.append(full)
            content = content.replace(tofind, torep)
            modif = True

        # js
        repl = {'https://unpkg.com/@jupyter-widgets/html-manager@^0.20.0/dist/embed-amd.js':
                '../_static/embed-amd.js'}
        lines = content.split('\n')
        new_lines = []
        for line in lines:
            if "https://cdnjs.cloudflare.com/ajax/libs/require.js" in line:
                if fLOG:
                    fLOG(
                        "[post_process_html_nb_output_static_file] js: skip %r" % line)
                modif = True
                continue
            new_lines.append(line)
        content = "\n".join(new_lines)
        for k, v in repl.items():
            if k in content:
                if fLOG:
                    fLOG("[post_process_html_output] js: replace %r -> %r" % (k, v))
                content = content.replace(k, v)
                modif = True

        if modif:
            fLOG("[post_process_html_nb_output_static_file] %r" % full)
            with open(full, "w", encoding="utf8") as f:
                f.write(content)

    return res
