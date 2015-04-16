"""
@file
@brief  Helper to convert a script written in Python 3 to Python 2

.. versionadded:: 1.0
"""

import os
import re
import shutil
from ..filehelper.synchelper import explore_folder_iterfile
from ..loghelper.flog import noLOG


def py3to2_convert_tree(folder,
                        dest,
                        encoding="utf8",
                        pattern=".*[.]py$",
                        pattern_copy=".*[.]((ico)|(dll)|(rst)|(ipynb)|(png)|(txt)|(zip)|(gz))$",
                        fLOG=noLOG):
    """
    Converts a tree from python 3 to python 2,
    the function only considers python script (verifying *pattern*).

    @param      folder          folder
    @param      dest            destination
    @param      encoding        all files will be saved with this encoding
    @param      pattern         pattern to find source code
    @param      pattern_copy    copy these files, do not modify them
    @parm       fLOG            logging function
    @return                     list of copied files

    If a folder does not exists, it will create it.
    The function excludes all files in subfolders
    starting by ``dist``, ``_doc``, ``build``, ``extensions``, ``nbextensions``.
    The function also exclude subfolders inside
    subfolders following the pattern ``ut_.*``.

    There are some issues difficult to solve with strings.
    Python 2.7 is not friendly with strings. Some needed pieces of code::

        if sys.version_info[0]==2:
            from codecs import open

    You can also read blog post :ref:`b-migration-py2py3`.

    .. versionadded:: 1.0
    """
    exclude = "temp_", "dist", "_doc", "build", "extensions", "nbextensions", "dist_module27"
    reg = re.compile(".*/ut_.*/.*/.*")

    conv = []
    for file in explore_folder_iterfile(folder, pattern=pattern):
        full = os.path.join(folder, file)
        file = os.path.relpath(file, folder)

        # undesired sub folders
        ex = False
        for exc in exclude:
            if file.startswith(exc) or "\\temp_" in file or \
               "/temp_" in file or "dist_module27" in file:
                ex = True
                break
        if ex:
            continue

        # subfolders inside unit tests folder
        lfile = file.replace("\\", "/")
        if reg.search(lfile):
            continue

        py2 = py3to2_convert(full)
        destfile = os.path.join(dest, file)
        dirname = os.path.dirname(destfile)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        with open(destfile, "w", encoding="utf8") as f:
            f.write(py2)
        conv.append(destfile)

    for file in explore_folder_iterfile(folder, pattern=pattern_copy):
        full = os.path.join(folder, file)
        file = os.path.relpath(file, folder)

        # undesired sub folders
        ex = False
        for exc in exclude:
            if file.startswith(exc) or "\\temp_" in file or \
               "/temp_" in file or "dist_module27" in file:
                ex = True
                break
        if ex:
            continue

        destfile = os.path.join(dest, file)
        dirname = os.path.dirname(destfile)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        shutil.copy(full, destfile)
        conv.append(destfile)

    fLOG("py3to2_convert_tree, copied", len(conv), "files")

    return conv


def py3to2_convert(script):
    """
    converts a script into from python 3 to python 2

    @param      script      script of filename
    @return                 string

    .. versionadded:: 1.0
    """
    if os.path.exists(script):
        try:
            with open(script, "r", encoding="utf8") as f:
                content = f.read()
        except UnicodeEncodeError:
            with open(script, "r") as f:
                content = f.read()

    else:
        content = script

    # start processing
    content = py3to2_remove_raise_from(content)

    # some other modification
    content = content.replace("from queue import", "from Queue import")

    # long and unicode
    content = content.replace("int  #long#", "long")
    content = content.replace("int  # long#", "long")
    content = content.replace("str  #unicode#", "unicode")
    content = content.replace("str  # unicode#", "unicode")

    # end
    return content


def py3to2_remove_raise_from(content):
    """
    Removes expression such as: ``raise Exception ("...") from e``.
    The function is very basic. It should be done with a grammar.

    @param      content     file content
    @return                 script
    """
    lines = content.split("\n")
    r = None
    for i, line in enumerate(lines):
        if " raise " in line:
            r = i
        if " from " in line and r is not None:
            spl = line.split(" from ")
            if len(spl[0].strip(" \n")) > 0:
                lines[i] = line = spl[0] + "# from " + " - ".join(spl[1:])

        if r is not None and i > r + 3:
            r = None

    return "\n".join(lines)
