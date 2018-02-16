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


def get_temp_folder(thisfile, name=None, clean=True, create=True, max_path=False, max_path_name="tpath"):
    """
    Creates and returns a local temporary folder to store files when unit testing.

    @param      thisfile        use ``__file__`` or the function which runs the test
    @param      name            name of the temporary folder
    @param      clean           if True, clean the folder first, it can also a function
                                called to determine whether or not the folder should be
                                cleaned
    @param      create          if True, creates it (empty if clean is True)
    @param      max_path        create a folder at root level to reduce path length,
                                the function checks the ``MAX_PATH`` variable and
                                shorten the test folder is *max_path* is True on Windows
                                or ``'force'`` on any OS.
    @param      max_path_name   test path used when *max_path* is True
    @return                     temporary folder

    .. versionadded:: 0.9

    .. versionchanged:: 1.5
        Parameter *thisfile* can be a function or a method.
        The function will extract the file which runs this test and will name
        the temporary folder base on the name of the method. *name* must be None.
        Parameters *max_path*, *max_path_name* were added to change the location to
        ``\\max_path_name`` if the ``MAX_PATH`` might be reached (on Windows)

    .. versionchanged:: 1.7
        Parameter *clean* can be a function.
        Signature is ``def clean(folder)``.
    """
    if name is None:
        name = thisfile.__name__
        if name.startswith("test_"):
            name = "temp_" + name[5:]
        elif not name.startswith("temp_"):
            name = "temp_" + name
        thisfile = os.path.abspath(thisfile.__func__.__code__.co_filename)
    final = os.path.split(name)[-1]

    if not final.startswith("temp_"):
        raise NameError("the folder '{0}' must begin with temp_".format(name))

    local = os.path.join(
        os.path.normpath(os.path.abspath(os.path.dirname(thisfile))), name)

    if max_path == "force" or sys.platform.startswith("win") and max_path:
        from ctypes.wintypes import MAX_PATH
        if MAX_PATH <= 300:
            local = os.path.join(os.path.abspath("\\" + max_path_name), name)

    if name == local:
        raise NameError(
            "The folder '{0}' must be relative, not absolute".format(name))

    if not os.path.exists(local):
        if create:
            os.mkdir(local)
            mode = os.stat(local).st_mode
            nmode = mode | stat.S_IWRITE
            if nmode != mode:
                os.chmod(local, nmode)
    else:
        if (callable(clean) and clean(local)) or (not callable(clean) and clean):
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
    Check if :epkg:`PEP8`,
    the function calls command :epkg:`pycodestyle`
    on a specific folder

    @param      folder              folder to look into
    @param      ignore              list of warnings to skip when raising an exception if
                                    PEP8 is not verified, see also
                                    `Error Codes <http://pep8.readthedocs.org/en/latest/intro.html#error-codes>`_
    @param      complexity          see `check_file <http://pycodestyle.readthedocs.io/en/latest/api.html?highlight=styleguide#pycodestyle.StyleGuide.check_files>`_
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
    printed by flake8 or pycodestyle.

    .. versionadded:: 1.4
    """
    import pycodestyle
    from pyflakes.api import checkPath as check_code
    from pyflakes.reporter import Reporter

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
        if file is None:
            raise TypeError("file cannot be None")
        if len(file) == 0:
            raise TypeError("file cannot be empty")
        try:
            style = pycodestyle.StyleGuide(
                ignore=ig, complexity=complexity, format='pylint')
            res = style.check_files([file])
        except TypeError as e:
            ext = "This is often due to an instruction from . import... The imported module has no name."
            raise TypeError("Issue with flake8 or pycodesyle for module '{0}' ig={1} complexity={2}\n{3}".format(
                file, ig, complexity, ext)) from e

        if not file.endswith("__init__.py"):
            flake_out = StringIO()
            flake_err = StringIO()
            reporter = Reporter(flake_out, flake_err)
            check_code(file, reporter=reporter)
            sys.stdout.write(flake_out.getvalue())
            sys.stdout.write(flake_err.getvalue())

        if extended is not None:
            with open(file, "r", errors="ignore") as f:
                content = f.readlines()
            extended_checkings(file, content, buf, extended)
        if res.total_errors + res.file_errors > 0:
            res.print_filename = True
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
    py27 = False
    if spl[-1].startswith("ut_"):
        if "dist_module27" in root:
            # python 27
            py27 = True
            newroot = os.path.join(root, "..", "..", "..", "..")
        else:
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
            raise FileNotFoundError("unable to find a subfolder '{0}' in '{1}' (py27={3})\nFOUND:\n{2}".format(
                name, newroot, "\n".join(dirs), py27))

        if py27:
            this = os.path.join(newroot, name, "dist_module27", "src")
        else:
            this = os.path.join(newroot, name, "src")

        if not os.path.exists(this):
            raise FileNotFoundError("unable to find a subfolder '{0}' in '{1}' (*py27={3})\nFOUND:\n{2}".format(
                this, newroot, "\n".join(dirs), py27))
        sys.path.append(this)
        if hide:
            with warnings.catch_warnings(record=True):
                importlib.import_module(name)
        else:
            importlib.import_module(name)
        paths.append(this)
    return paths
