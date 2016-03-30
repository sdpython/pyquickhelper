"""
@file
@brief This extension contains various functionalities to help unittesting.

.. versionadded:: 1.4
    Split from from utils_tests.py.
"""
from __future__ import print_function

import os
import stat
import sys
import re
import warnings
import time
import importlib

from ..filehelper.synchelper import remove_folder, explore_folder_iterfile
from ..loghelper.flog import noLOG

if sys.version_info[0] == 2:
    from StringIO import StringIO
    FileNotFoundError = Exception
else:
    from io import StringIO


def get_temp_folder(thisfile, name, clean=True, create=True):
    """
    return a local temporary folder to store files when unit testing

    @param      thisfile        use ``__file__``
    @param      name            name of the temporary folder
    @param      clean           if True, clean the folder first
    @param      create          if True, creates it (empty if clean is True)
    @return                     temporary folder

    .. versionadded:: 0.9
    """
    if not name.startswith("temp_"):
        raise NameError("the folder {0} must begin with temp_".format(name))

    local = os.path.join(
        os.path.normpath(os.path.abspath(os.path.dirname(thisfile))), name)
    if name == local:
        raise NameError(
            "the folder {0} must be relative, not absolute".format(name))

    if not os.path.exists(local):
        if create:
            os.mkdir(local)
            mode = os.stat(local).st_mode
            nmode = mode | stat.S_IWRITE
            if nmode != mode:
                os.chmod(local, nmode)
    else:
        if clean:
            remove_folder(local)
            time.sleep(0.1)
        if create and not os.path.exists(local):
            os.mkdir(local)
            mode = os.stat(local).st_mode
            nmode = mode | stat.S_IWRITE
            if nmode != mode:
                os.chmod(local, nmode)

    return local


def _extended_refactoring(filename, line):
    """
    Private function to do extra checkings when refactoring pyquickhelper

    @param      filename        filename
    @param      line            line
    @return                     None or error message
    """
    if "from pyquickhelper import fLOG" in line:
        if "test_flake8" not in filename:
            return "issue with fLOG"
    if "from pyquickhelper import noLOG" in line:
        if "test_flake8" not in filename:
            return "issue with noLOG"
    if "from pyquickhelper import run_cmd" in line:
        if "test_flake8" not in filename:
            return "issue with run_cmd"
    if "from pyquickhelper import get_temp_folder" in line:
        if "test_flake8" not in filename:
            return "issue with get_temp_folder"
    return None


def check_pep8(folder, ignore=('E501', 'E265'), skip=None,
               complexity=-1, stop_after=100, fLOG=noLOG,
               neg_filter=None, extended=None, max_line_length=162):
    """
    Check if `PEP8 <https://www.python.org/dev/peps/pep-0008/>`_,
    the function calls command `flake8 <https://flake8.readthedocs.org/en/latest/>`_
    on a specific folder

    @param      folder              folder to look into
    @param      ignore              list of warnings to skip when raising an exception if
                                    PEP8 is not verified, see also
                                    `Error Codes <http://pep8.readthedocs.org/en/latest/intro.html#error-codes>`_
    @param      complexity          see `check_file <http://flake8.readthedocs.org/en/latest/api.html#flake8.main.check_file>`_
    @param      stop_after          stop after *stop_after* issues
    @param      skip                skip a warning if a substring in this list is found
    @param      neg_filter          skip files verifying this regular expressions
    @param      extended            list of tuple (name, function), see below
    @param      max_line_length     maximum allowed length of a line of code
    @param      fLOG                logging function
    @return                         out

    Functions mentioned in *extended* takes two parameters (file name and line)
    and they returned None or an error message or a tuple (position in the line, error message).
    When the return is not empty, a warning will be added to the ones
    printed by flake8.

    .. versionadded:: 1.4
    """
    from flake8.main import check_file

    def extended_checkings(fname, content, buf, extended):
        for i, line in enumerate(content):
            for name, fu in extended:
                r = fu(fname, line)
                if isinstance(r, tuple):
                    c, r = r
                else:
                    c = 1
                if r is not None:
                    buf.write("{0}:{1}:{4} F{2} {3}\n".format(
                        fname, i + 1, name, r, c))

    def fkeep(s):
        if len(s) == 0:
            return False
        if skip is not None:
            for kip in skip:
                if kip in s:
                    return False
        return True

    if max_line_length is not None:
        if extended is None:
            extended = []
        else:
            extended = extended.copy()

        def check_lenght_line(fname, line):
            if len(line) > max_line_length and not line.lstrip().startswith('#'):
                if ">`_" in line or ":math:`" in line or "ERROR: " in line:
                    # we skip line containing url or comments
                    pass
                else:
                    return "line too long {0} > {1}".format(len(line), max_line_length)
            return None

        extended.append(("ECL1", check_lenght_line))

    if ignore is None:
        ignore = tuple()
    elif isinstance(ignore, list):
        ignore = tuple(ignore)

    regneg_filter = None if neg_filter is None else re.compile(neg_filter)

    stdout = sys.stdout
    buf = StringIO()
    sys.stdout = buf
    for file in explore_folder_iterfile(folder, pattern=".*[.]py$"):
        if regneg_filter is not None:
            if regneg_filter.search(file):
                continue
        if file.endswith("__init__.py"):
            ig = ignore + ('F401',)
        else:
            ig = ignore
        res = check_file(file, ignore=ig, complexity=complexity)
        if extended is not None:
            with open(file, "r", errors="ignore") as f:
                content = f.readlines()
            extended_checkings(file, content, buf, extended)
        if res > 0:
            lines = [_ for _ in buf.getvalue().split("\n") if fkeep(_)]
            if len(lines) > stop_after:
                raise Exception(
                    "{0} lines\n{1}".format(len(lines), "\n".join(lines)))
    sys.stdout = stdout

    lines = [_ for _ in buf.getvalue().split("\n") if fkeep(_)]
    if len(lines) > 0:
        raise Exception(
            "{0} lines\n{1}".format(len(lines), "\n".join(lines)))
    return "\n".join(lines)


def add_missing_development_version(names, root, hide=False):
    """
    look for development version of a given module and add paths to
    ``sys.path`` after having checked they are working

    @param      names           name or names of the module to import
    @param      root            folder where to look (assuming all modules location
                                at the same place in a flat hierarchy)
    @param      hide            hide warnings when importing a module (might be a lot)
    @return                     added paths

    .. versionadded:: 1.4
    """
    if not isinstance(names, list):
        names = [names]
    root = os.path.abspath(root)
    if os.path.isfile(root):
        root = os.path.dirname(root)
    if not os.path.exists(root):
        raise FileNotFoundError(root)
    spl = os.path.split(root)
    if spl[-1].startswith("ut_"):
        newroot = os.path.join(root, "..", "..", "..")
    else:
        newroot = root
    newroot = os.path.normpath(os.path.abspath(newroot))
    found = os.listdir(newroot)
    dirs = [os.path.join(newroot, _) for _ in found]

    paths = []
    for name in names:
        try:
            importlib.import_module(name)
            continue
        except ImportError:
            # it requires a path
            pass
        if name not in found:
            raise FileNotFoundError("unable to find a subfolder '{0}' in '{1}'\nFOUND:\n{2}".format(
                name, newroot, "\n".join(dirs)))
        this = os.path.join(newroot, name, "src")
        if not os.path.exists(this):
            raise FileNotFoundError("unable to find a subfolder '{0}' in '{1}'\nFOUND:\n{2}".format(
                this, newroot, "\n".join(dirs)))
        sys.path.append(this)
        if hide:
            with warnings.catch_warnings(record=True):
                importlib.import_module(name)
        else:
            importlib.import_module(name)
        paths.append(this)
    return paths
