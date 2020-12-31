"""
@file
@brief  Helper to convert a script written in Python 3 to Python 2
"""

import os
import re
import shutil
from ..filehelper.synchelper import explore_folder_iterfile
from ..loghelper.flog import noLOG
from .default_regular_expression import _setup_pattern_copy


class Convert3to2Exception(Exception):

    """
    exception raised for an exception happening during the conversion
    """
    pass


def py3to2_convert_tree(folder, dest, encoding="utf8", pattern=".*[.]py$",
                        pattern_copy=_setup_pattern_copy,
                        unittest_modules=None, fLOG=noLOG):
    """
    Converts files in a folder and its subfolders from python 3 to python 2,
    the function only considers python script (verifying *pattern*).

    @param      folder              folder
    @param      dest                destination
    @param      encoding            all files will be saved with this encoding
    @param      pattern             pattern to find source code
    @param      pattern_copy        copy these files, do not modify them
    @param      fLOG                logging function
    @param      unittest_modules    modules used during unit tests but not installed
    @return                         list of copied files

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

    The variable *unittest_modules* indicates the list of
    modules which are not installed in :epkg:`Python` distribution
    but still used and placed in the same folder as the same which
    has to converted.

    *unittest_modules* can be either a list or a tuple ``(module, alias)``.
    Then the alias appears instead of the module name.

    The function does not convert the exception
    `FileNotFoundError <https://docs.python.org/3/library/exceptions.html>`_
    which only exists in Python 3. The module will fail in version 2.7
    if this exception is raised.

    The following page
    `Cheat Sheet: Writing Python 2-3 compatible code
    <http://python-future.org/compatible_idioms.html>`_
    gives the difference between the two versions of Python
    and how to write compatible code.
    """
    exclude = ("temp_", "dist", "_doc", "build", "extensions",
               "nbextensions", "dist_module27", "_virtualenv", "_venv")
    reg = re.compile(".*/ut_.*/.*/.*")

    conv = []
    for file in explore_folder_iterfile(folder, pattern=pattern):
        full = os.path.join(folder, file)
        if "site-packages" in full:
            continue
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

        py2 = py3to2_convert(full, unittest_modules)
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
        shutil.copy(full, dirname)
        conv.append(destfile)

    fLOG("py3to2_convert_tree, copied", len(conv), "files")

    return conv


def py3to2_convert(script, unittest_modules):
    """
    converts a script into from python 3 to python 2

    @param      script              script or filename
    @param      unittest_modules    modules used during unit test but not installed,
                                    @see fn py3to2_convert_tree
    @return                         string

    See see @fn py3to2_convert_tree for more information.
    """
    if os.path.exists(script):
        try:
            with open(script, "r", encoding="utf8") as f:
                content = f.read()
        except (UnicodeEncodeError, UnicodeDecodeError):  # pragma: no cover
            with open(script, "r") as f:
                content = f.read()

    else:
        content = script  # pragma: no cover

    # start processing
    content = py3to2_remove_raise_from(content)

    # unicode
    if ("install_requires=" in content or "package_data" in content) and "setup" in content:
        # we skip the file setup.py as it raises an error
        pass
    else:
        try:
            content = py3to2_future(content)
        except Convert3to2Exception as e:  # pragma: no cover
            raise Convert3to2Exception(
                'unable to convert a file due to unicode issue.\n  File "{0}", line 1'.format(script)) from e

    # some other modification
    content = content.replace("from queue import", "from Queue import")
    content = content.replace("nonlocal ", "# nonlocal ")

    # long and unicode
    content = content.replace("int  #long#", "long")
    content = content.replace("int  # long#", "long")
    content = content.replace("str  #unicode#", "unicode")
    content = content.replace("str  # unicode#", "unicode")
    content = content.replace(
        "Programming Language :: Python :: 3", "Programming Language :: Python :: 2")
    content = content.replace(', sep="\\t")', ', sep="\\t".encode("ascii"))')

    # imported modules
    if unittest_modules is not None:
        content = py3to2_imported_local_modules(content, unittest_modules)

    # end
    return content


def py3to2_future(content):
    """
    checks that import ``from __future__ import unicode_literals``
    is always present, the function assumes it is a python code

    @param      content     file content
    @return                 new content
    """
    find = "from __future__ import unicode_literals"
    if find in content and '"{0}"'.format(find) not in content:
        # the second condition avoid to raise this
        # exception when parsing this file
        # this case should only happen for this file
        raise Convert3to2Exception(  # pragma: no cover
            "unable to convert a file")

    lines = content.split("\n")
    position = 0
    incomment = None
    while (position < len(lines) and not lines[position].startswith("import ") and
            not lines[position].startswith("from ") and
            not lines[position].startswith("def ") and
            not lines[position].startswith("class ")):
        if incomment is None:
            if lines[position].startswith("'''"):
                incomment = "'''"  # pragma: no cover
            elif lines[position].startswith('"""'):
                incomment = '"""'
        else:
            if lines[position].endswith("'''"):  # pragma: no cover
                incomment = None
                position += 1
                break
            if lines[position].endswith('"""'):
                incomment = None
                position += 1
                break
        position += 1

    if position < len(lines):
        lines[position] = "{0}\n{1}".format(find, lines[position])
    return "\n".join(lines)


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


def py3to2_imported_local_modules(content, unittest_modules):
    """
    See function @see fn py3to2_convert_tree
    and documentation about parameter *unittest_modules*.

    @param      content             script or filename
    @param      unittest_modules    modules used during unit test but not installed,
                                    @see fn py3to2_convert_tree
    """
    lines = content.split("\n")
    for modname in unittest_modules:
        if isinstance(modname, tuple):
            modname, alias = modname  # pragma: no cover
        else:
            alias = modname

        s1 = '"{0}"'.format(modname)
        s2 = "'{0}'".format(modname)
        s3 = "import {0}".format(modname)
        s4 = '"{0}"'.format(modname.upper())
        s4_rep = '"{0}27"'.format(modname.upper())

        if (s1 in content or s2 in content or s4 in content) and s3 in content:
            for i, line in enumerate(lines):
                if " in " in line or "ModuleInstall" in line:
                    continue
                if s1 in line:
                    line = line.replace(
                        s1, '"..", "{0}", "dist_module27"'.format(alias))
                    lines[i] = line
                elif s2 in line:
                    line = line.replace(  # pragma: no cover
                        s2, "'..', '{0}', 'dist_module27'".format(alias))
                    lines[i] = line  # pragma: no cover
                elif s4 in line:
                    line = line.replace(s4, s4_rep)
                    lines[i] = line
    return "\n".join(lines)
