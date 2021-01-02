"""
@file
@brief This extension contains various functionalities to help unittesting.
"""
import os
import stat
import sys
import re
import warnings
import time
import importlib
from contextlib import redirect_stdout, redirect_stderr
from io import StringIO


def _get_PyLinterRunV():
    # Separate function to speed up import.
    from pylint.lint import Run as PyLinterRun
    from pylint import __version__ as pylint_version
    if pylint_version >= '2.0.0':
        PyLinterRunV = PyLinterRun
    else:
        PyLinterRunV = lambda *args, do_exit=False: PyLinterRun(  # pylint: disable=E1120, E1123
            *args, exit=do_exit)  # pylint: disable=E1120, E1123
    return PyLinterRunV


def get_temp_folder(thisfile, name=None, clean=True, create=True,
                    persistent=False, path_name="tpath"):
    """
    Creates and returns a local temporary folder to store files
    when unit testing.

    @param      thisfile        use ``__file__`` or the function which runs the test
    @param      name            name of the temporary folder
    @param      clean           if True, clean the folder first, it can also a function
                                called to determine whether or not the folder should be
                                cleaned
    @param      create          if True, creates it (empty if clean is True)
    @param      persistent      if True, create a folder at root level to reduce path length,
                                the function checks the ``MAX_PATH`` variable and
                                shorten the test folder is *max_path* is True on :epkg:`Windows`,
                                on :epkg:`Linux`, it creates a folder three level ahead
    @param      path_name       test path used when *max_path* is True
    @return                     temporary folder

    The function extracts the file which runs this test and will name
    the temporary folder base on the name of the method. *name* must be None.

    .. versionchanged:: 1.7
        Parameter *clean* can be a function.
        Signature is ``def clean(folder)``.

    .. versionchanged:: 1.8
        Renames parameters *max_path* and *max_path_name*.
    """
    if name is None:
        name = thisfile.__name__
        if name.startswith("test_"):
            name = "temp_" + name[5:]
        elif not name.startswith("temp_"):
            name = "temp_" + name
        thisfile = os.path.abspath(thisfile.__func__.__code__.co_filename)
    final = os.path.split(name)[-1]

    if not final.startswith("temp_") and not final.startswith("temp2_"):
        raise NameError("the folder '{0}' must begin with temp_".format(name))

    local = os.path.join(
        os.path.normpath(os.path.abspath(os.path.dirname(thisfile))), name)

    if persistent:
        if sys.platform.startswith("win"):
            from ctypes.wintypes import MAX_PATH
            if MAX_PATH <= 300:
                local = os.path.join(os.path.abspath("\\" + path_name), name)
            else:
                local = os.path.join(
                    local, "..", "..", "..", "..", path_name, name)
        else:
            local = os.path.join(local, "..", "..", "..",
                                 "..", path_name, name)
        local = os.path.normpath(local)

    if name == local:
        raise NameError(
            "The folder '{0}' must be relative, not absolute".format(name))

    if not os.path.exists(local):
        if create:
            os.makedirs(local)
            mode = os.stat(local).st_mode
            nmode = mode | stat.S_IWRITE
            if nmode != mode:
                os.chmod(local, nmode)
    else:
        if (callable(clean) and clean(local)) or (not callable(clean) and clean):
            # delayed import to speed up import time of pycode
            from ..filehelper.synchelper import remove_folder
            remove_folder(local)
            time.sleep(0.1)
        if create and not os.path.exists(local):
            os.makedirs(local)
            mode = os.stat(local).st_mode
            nmode = mode | stat.S_IWRITE
            if nmode != mode:
                os.chmod(local, nmode)

    return local


def _extended_refactoring(filename, line):
    """
    Private function which does extra checkings
    when refactoring :epkg:`pyquickhelper`.

    @param      filename        filename
    @param      line            line
    @return                     None or error message
    """
    if "from pyquickhelper import fLOG" in line:
        if "test_code_style" not in filename:
            return "issue with fLOG"
    if "from pyquickhelper import noLOG" in line:
        if "test_code_style" not in filename:
            return "issue with noLOG"
    if "from pyquickhelper import run_cmd" in line:
        if "test_code_style" not in filename:
            return "issue with run_cmd"
    if "from pyquickhelper import get_temp_folder" in line:
        if "test_code_style" not in filename:
            return "issue with get_temp_folder"
    return None


class PEP8Exception(Exception):
    """
    Code or style issues.
    """
    pass


def check_pep8(folder, ignore=('E265', 'W504'), skip=None,
               complexity=-1, stop_after=100, fLOG=None,
               pylint_ignore=('C0103', 'C1801',
                              'R0201', 'R1705',
                              'W0108', 'W0613',
                              'W0107', 'C0415'),
               recursive=True, neg_pattern=None, extended=None,
               max_line_length=143, pattern=".*[.]py$",
               run_lint=True, verbose=False, run_cmd_filter=None):
    """
    Checks if :epkg:`PEP8`,
    the function calls command :epkg:`pycodestyle`
    on a specific folder.

    @param      folder              folder to look into
    @param      ignore              list of warnings to skip when raising an exception if
                                    :epkg:`PEP8` is not verified, see also
                                    `Error Codes <http://pep8.readthedocs.org/en/latest/intro.html#error-codes>`_
    @param      pylint_ignore       ignore :epkg:`pylint` issues, see
                                    `pylint error codes <http://pylint-messages.wikidot.com/all-codes>`_
    @param      complexity          see `check_file <http://pycodestyle.readthedocs.io/en/latest/api.html
                                    ?highlight=styleguide#pycodestyle.StyleGuide.check_files>`_
    @param      stop_after          stop after *stop_after* issues
    @param      skip                skip a warning if a substring in this list is found
    @param      neg_pattern         skip files verifying this regular expressions
    @param      extended            list of tuple (name, function), see below
    @param      max_line_length     maximum allowed length of a line of code
    @param      recursive           look into subfolder
    @param      pattern             only file matching this pattern will be checked
    @param      run_lint            run :epkg:`pylint`
    @param      verbose             :epkg:`pylint` is slow, tells which file is
                                    investigated (but it is even slower)
    @param      run_cmd_filter      some files makes :epkg:`pylint` crashes (``import yaml``),
                                    the test for this is run in a separate process
                                    if the function *run_cmd_filter* returns True of the filename,
                                    *verbose* is set to True in that case
    @param      fLOG                logging function
    @return                         output

    Functions mentioned in *extended* takes two parameters (file name and line)
    and they returned None or an error message or a tuple (position in the line, error message).
    When the return is not empty, a warning will be added to the ones
    printed by :epkg:`pycodestyle`.
    A few codes to ignore:

    * *E501*: line too long (?? characters)
    * *E265*: block comments should have a space after #
    * *W504*: line break after binary operator, this one is raised
      after the code is modified by @see fn remove_extra_spaces_and_pep8.

    The full list is available at :epkg:`PEP8 codes`. In addition,
    the function adds its own codes:

    * *ECL1*: line too long for a specific reason.

    Some errors to disable with :epkg:`pylint`:

    * *C0103*: variable name is not conform
    * *C0111*: missing function docstring
    * *C1801*: do not use `len(SEQUENCE)` to determine if a sequence is empty
    * *R0201*: method could be a function
    * *R0205*: Class '?' inherits from object, can be safely removed from bases in python3 (pylint)
    * *R0901*: too many ancestors
    * *R0902*: too many instance attributes
    * *R0911*: too many return statements
    * *R0912*: too many branches
    * *R0913*: too many arguments
    * *R0914*: too many local variables
    * *R0915*: too many statements
    * *R1702*: too many nested blocks
    * *R1705*: unnecessary "else" after "return"
    * *W0107*: unnecessary pass statements
    * *W0108*: Lambda may not be necessary
    * *W0613*: unused argument

    The full list is available at :epkg:`pylint error codes`.
    :epkg:`pylint` was added used to check the code.
    It produces the following list of errors
    :epkg:`pylint error codes`.

    .. versionchanged:: 1.8
        If *neg_pattern* is empty, it populates with a default value
        which skips unnecessary folders:
        ``".*[/\\\\\\\\]((_venv)|([.]git)|(__pycache__)|(temp_)).*"``.
    """
    # delayed import to speed up import time of pycode
    import pycodestyle
    from ..filehelper.synchelper import explore_folder_iterfile
    if fLOG is None:
        from ..loghelper.flog import noLOG
        fLOG = noLOG

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
                if ">`_" in line:
                    return "line too long (link) {0} > {1}".format(len(line), max_line_length)
                if ":math:`" in line:
                    return "line too long (:math:) {0} > {1}".format(len(line), max_line_length)
                if "ERROR: " in line:
                    return "line too long (ERROR:) {0} > {1}".format(len(line), max_line_length)
            return None

        extended.append(("[ECL1]", check_lenght_line))

    if ignore is None:
        ignore = tuple()
    elif isinstance(ignore, list):
        ignore = tuple(ignore)

    if neg_pattern is None:
        neg_pattern = ".*[/\\\\]((_venv)|([.]git)|(__pycache__)|(temp_)|([.]egg)|(bin)).*"

    try:
        regneg_filter = None if neg_pattern is None else re.compile(
            neg_pattern)
    except re.error as e:
        raise ValueError("Unable to compile '{0}'".format(neg_pattern)) from e

    # pycodestyle
    fLOG("[check_pep8] code style on '{0}'".format(folder))
    files_to_check = []
    skipped = []
    buf = StringIO()
    with redirect_stdout(buf):
        for file in explore_folder_iterfile(folder, pattern=pattern,
                                            recursive=recursive):
            if regneg_filter is not None:
                if regneg_filter.search(file):
                    skipped.append(file)
                    continue
            if file.endswith("__init__.py"):
                ig = ignore + ('F401',)
            else:
                ig = ignore
            if file is None:
                raise TypeError("file cannot be None")
            if len(file) == 0:
                raise TypeError("file cannot be empty")

            # code style
            files_to_check.append(file)
            try:
                style = pycodestyle.StyleGuide(
                    ignore=ig, complexity=complexity, format='pylint',
                    max_line_length=max_line_length)
                res = style.check_files([file])
            except TypeError as e:
                ext = "This is often due to an instruction from . import... The imported module has no name."
                raise TypeError("Issue with pycodesyle for module '{0}' ig={1} complexity={2}\n{3}".format(
                    file, ig, complexity, ext)) from e

            if extended is not None:
                with open(file, "r", errors="ignore") as f:
                    content = f.readlines()
                extended_checkings(file, content, buf, extended)

            if res.total_errors + res.file_errors > 0:
                res.print_filename = True
                lines = [_ for _ in buf.getvalue().split("\n") if fkeep(_)]
                if len(lines) > stop_after:
                    raise PEP8Exception(
                        "{0} lines\n{1}".format(len(lines), "\n".join(lines)))

    lines = [_ for _ in buf.getvalue().split("\n") if fkeep(_)]
    if len(lines) > 10:
        raise PEP8Exception(
            "{0} lines\n{1}".format(len(lines), "\n".join(lines)))

    if len(files_to_check) == 0:
        mes = skipped[0] if skipped else "-no skipped file-"
        raise FileNotFoundError("No file found in '{0}'\n pattern='{1}'\nskipped='{2}'".format(
                                folder, pattern, mes))

    # pylint
    if not run_lint:
        return "\n".join(lines)
    fLOG("[check_pep8] pylint with {0} files".format(len(files_to_check)))
    memout = sys.stdout

    try:
        fLOG('', OutputStream=memout)
        regular_print = False
    except TypeError:
        regular_print = True

    def myprint(s):
        "local print, chooses the right function"
        if regular_print:
            memout.write(s + "\n")
        else:
            fLOG(s, OutputStream=memout)

    neg_pat = ".*temp[0-9]?_.*,doc_.*"
    if neg_pattern is not None:
        neg_pat += ',' + neg_pattern

    if run_cmd_filter is not None:
        verbose = True

    PyLinterRunV = _get_PyLinterRunV()
    sout = StringIO()
    serr = StringIO()
    with redirect_stdout(sout):
        with redirect_stderr(serr):
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", DeprecationWarning)
                opt = ["--ignore-patterns=" + neg_pat, "--persistent=n",
                       '--jobs=1', '--suggestion-mode=n', "--score=n",
                       '--max-args=30', '--max-locals=50', '--max-returns=30',
                       '--max-branches=50', '--max-parents=25',
                       '--max-attributes=50', '--min-public-methods=0',
                       '--max-public-methods=100', '--max-bool-expr=10',
                       '--max-statements=200',
                       '--msg-template={abspath}:{line}: {msg_id}: {msg} (pylint)']
                if pylint_ignore:
                    opt.append('--disable=' + ','.join(pylint_ignore))
                if max_line_length:
                    opt.append("--max-line-length=%d" % max_line_length)
                if verbose:
                    for i, name in enumerate(files_to_check):
                        cop = list(opt)
                        cop.append(name)
                        if run_cmd_filter is None or not run_cmd_filter(name):
                            myprint(
                                "[check_pep8] lint file {0}/{1} - '{2}'\n".format(i + 1, len(files_to_check), name))
                            PyLinterRunV(cop, do_exit=False)
                        else:
                            # delayed import to speed up import time of pycode
                            from ..loghelper import run_cmd
                            # runs from command line
                            myprint(
                                "[check_pep8] cmd-lint file {0}/{1} - '{2}'\n".format(i + 1, len(files_to_check), name))
                            cmd = "{0} -m pylint {1}".format(
                                sys.executable, " ".join('"{0}"'.format(_) for _ in cop))
                            out = run_cmd(cmd, wait=True)[0]
                            lines.extend(_ for _ in out.split(
                                '\n') if _.strip('\r '))
                else:
                    opt.extend(files_to_check)
                    PyLinterRunV(opt, do_exit=False)

    pylint_lines = sout.getvalue().split('\n')
    pylint_lines = [
        _ for _ in pylint_lines if (
            '(pylint)' in _ and fkeep(_) and _[0] != ' ' and len(_.split(':')) > 2)]
    pylint_lines = [_ for _ in pylint_lines if not _.startswith(
        "except ") and not _.startswith("else:") and not _.startswith(
        "try:") and "# noqa" not in _]
    lines.extend(pylint_lines)
    if len(lines) > 0:
        raise PEP8Exception(
            "{0} lines\n{1}".format(len(lines), "\n".join(lines)))

    return "\n".join(lines)


def add_missing_development_version(names, root, hide=False):
    """
    Looks for development version of a given module and add paths to
    ``sys.path`` after having checked they are working.

    @param      names           name or names of the module to import
    @param      root            folder where to look (assuming all modules location
                                at the same place in a flat hierarchy)
    @param      hide            hide warnings when importing a module (might be a lot)
    @return                     added paths
    """
    # delayed import to speed up import time
    from ..loghelper import sys_path_append

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
        exc = None
        try:
            if hide:
                with warnings.catch_warnings(record=True):
                    importlib.import_module(name)
            else:
                importlib.import_module(name)
            continue
        except ImportError as e:
            # it requires a path
            exc = e

        if name not in found:
            raise FileNotFoundError("Unable to find a subfolder '{0}' in '{1}' (py27={3})\nFOUND:\n{2}\nexc={4}".format(
                name, newroot, "\n".join(dirs), py27, exc))

        if py27:
            this = os.path.join(newroot, name, "dist_module27", "src")
            if not os.path.exists(this):
                this = os.path.join(newroot, name, "dist_module27")
        else:
            this = os.path.join(newroot, name, "src")
            if not os.path.exists(this):
                this = os.path.join(newroot, name)

        if not os.path.exists(this):
            raise FileNotFoundError("unable to find a subfolder '{0}' in '{1}' (*py27={3})\nFOUND:\n{2}".format(
                this, newroot, "\n".join(dirs), py27))
        with sys_path_append(this):
            if hide:
                with warnings.catch_warnings(record=True):
                    importlib.import_module(name)
            else:
                importlib.import_module(name)
        paths.append(this)
    return paths
