"""
@file
@brief  Helper for the setup

.. todoext::
    :title: run unit test if their estimated time is below a certain threshold
    :hidden:
    :issue: 23
    :tag: enhancement
    :cost: 0.2
    :date: 2016-07-24

    Example::

        python setup.py unittests -d 1

    Run all unit test for which the estimated duration is below 1s.

.. versionadded:: 1.1
"""

import os
import sys
import re
import warnings
import hashlib
import datetime
from ..loghelper.pyrepo_helper import SourceRepository
from ..loghelper.flog import noLOG
from ..filehelper import get_url_content_timeout, explore_folder_iterfile
from .code_helper import remove_extra_spaces_folder
from .py3to2 import py3to2_convert_tree
from .build_helper import get_build_script, get_script_command, get_extra_script_command, get_script_module, get_pyproj_project
from .call_setup_hook import call_setup_hook
from .tkinter_helper import fix_tkinter_issues_virtualenv
from .default_regular_expression import _setup_pattern_copy
from ..ipythonhelper import upgrade_notebook, remove_execution_number
from .utils_tests import main_wrapper_tests, default_skip_function


if sys.version_info[0] == 2:
    from codecs import open


def available_commands_list(argv):
    """
    checks that on command handled by pyquickhelper is part of the arguments

    @param      argv        sys.arg
    @return                 bool
    """
    commands = {"bdist_msi", "build_script", "build_sphinx", "bdist_egg",
                "bdist_wheel", "bdist_wininst", "build_ext",
                "clean_pyd", "clean_space", "copy_dist",
                "copy27", "run27", "build27",
                "local_pypi", "test_local_pypi",
                "notebook", "publish", "publish_doc",
                "register", "unittests", "lab",
                "unittests_LONG", "unittests_SKIP", "unittests_GUI",
                "sdist", "setupdep", "upload_docs",
                "setup_hook", "copy_sphinx", "write_version"}
    for c in commands:
        if c in argv:
            return True
    return False


def process_standard_options_for_setup(argv, file_or_folder, project_var_name, module_name=None, unittest_modules=None,
                                       pattern_copy=_setup_pattern_copy,
                                       requirements=None, port=8067, blog_list=None, default_engine_paths=None,
                                       extra_ext=None, add_htmlhelp=False, setup_params=None, coverage_options=None,
                                       coverage_exclude_lines=None, func_sphinx_begin=None, func_sphinx_end=None,
                                       additional_notebook_path=None, additional_local_path=None, copy_add_ext=None,
                                       nbformats=(
                                           "ipynb", "html", "python", "rst", "slides",
                                           "pdf", "present", "github"),
                                       layout=None,  # , "epub"],
                                       additional_ut_path=None,
                                       skip_function=default_skip_function, covtoken=None, hook_print=True,
                                       stdout=None, stderr=None, use_run_cmd=False, filter_warning=None,
                                       file_filter_pep8=None, fLOG=noLOG):
    """
    Processes the standard options the module pyquickhelper is
    able to process assuming the module which calls this function
    follows the same design as *pyquickhelper*, it will process the following
    options:

    .. runpython::

        from pyquickhelper.pycode import process_standard_options_for_setup_help
        process_standard_options_for_setup_help("--help-commands")

    @param      argv                        = *sys.argv*
    @param      file_or_folder              file ``setup.py`` or folder which contains it
    @param      project_var_name            display name of the module
    @param      module_name                 module name, None if equal to *project_var_name* (``import <module_name>``)
    @param      unittest_modules            modules added for the unit tests, see @see fn py3to2_convert_tree
    @param      pattern_copy                see @see fn py3to2_convert_tree
    @param      requirements                dependencies, fetched with a local pipy server from ``http://localhost:port/``
    @param      port                        port for the local pipy server
    @param      blog_list                   list of blog to listen for this module (usually stored in ``module.__blog__``)
    @param      default_engine_paths        define the default location for python engine, should be dictionary *{ engine: path }*, see below.
    @param      extra_ext                   extra file extension to process (add a page for each of them, ex ``["doc"]``)
    @param      add_htmlhelp                run HTML Help too (only on Windows)
    @param      setup_params                parameters send to @see fn call_setup_hook
    @param      coverage_options            see @see fn main_wrapper_tests
    @param      coverage_exclude_lines      see @see fn main_wrapper_tests
    @param      func_sphinx_begin           function called before the documentation generation,
                                            it gets the same parameters as this function (all named),
                                            use ``**args**``
    @param      func_sphinx_end             function called after the documentation generation,
                                            it gets the same parameters as this function (all named),
                                            use ``**args**``
    @param      additional_notebook_path    additional paths to add when launching the notebook
    @param      additional_local_path       additional paths to add when running a local command
    @param      copy_add_ext                additional file extensions to copy
    @param      nbformats                   requested formats for the notebooks conversion
    @param      layout                      list of formats sphinx should generate such as html, latex, pdf, docx,
                                            it is a list of tuple (layout, build directory, parameters to override),
                                            if None --> ``["html", "pdf"]``
    @param      additional_ut_path          additional paths to add when running unit tests
    @param      skip_function               function to skip unit tests, see @ee fn main_wrapper_tests
    @param      covtoken                    token used when publishing coverage report to `codecov <https://codecov.io/>`_,
                                            more in @see fn main_wrapper_tests
    @param      fLOG                        logging function
    @param      hook_print                  enable, disable print when calling *_setup_hook*
    @param      stdout                      redirect stdout for unit test if not None
    @param      stderr                      redirect stderr for unit test  if not None
    @param      use_run_cmd                 to run the sphinx documentation with @see fn run_cmd and not ``os.system``
    @param      filter_warning              see @see fn main_wrapper_tests
    @param      file_filter_pep8            function to filter out files for which checking pep8
                                            (see @see fn remove_extra_spaces_folder)
    @return                                 True (an option was processed) or False,
                                            the file ``setup.py`` should call function ``setup``

    The command ``build_script`` is used, the flag ``--private`` can be used to
    avoid producing scripts to publish the module on `Pypi <https://pypi.python.org/pypi>`_.

    An example for *default_engine_paths*::

        default_engine_paths = {
            "windows": {
                "__PY34__": None,
                "__PY35__": None,
                "__PY36_X64__": "c:\\Python36_x64",
                "__PY35_X64__": "c:\\Python35_x64",
                "__PY34_X64__": "c:\\Python34_x64",
                "__PY27_X64__": "c:\\Anaconda2",
            },
        }

    Parameters *coverage_options*, *coverage_exclude_lines*, *copy_add_ext* were added
    for function @see fn main_wrapper_tests.
    Parameter *unittest_modules* accepts a list of string and 2-uple.
    If it is a 2-uple, the first string is used to convert Python 3 code into Python 2
    (in case the local folder is different from the module name),
    the second string is used to add local path to the variable ``PYTHON_PATH``.
    If it is a single string, it means both name strings are equal.
    Parameters *func_sphinx_begin* and *func_sphinx_end* were added
    to pre-process or post-process the documentation.
    Parameter *additional_notebook_path* was added to specify some additional
    paths when preparing the script *auto_cmd_notebook.bat*.
    Parameters *layout*, *nbformats* were added for
    function @see fn generate_help_sphinx.
    The coverage computation can be disable by specifying
    ``coverage_options["disable_coverage"] = True``.
    Parameter *covtoken* was added to post the coverage report to :epkg:`codecov`.
    Option ``-e`` and ``-g`` were added to
    filter file by regular expressions (in with *e*, out with *g*).

    .. versionchanged:: 1.5
        Parameter *file_filter_pep8* was added.
    """
    if layout is None:
        layout = ["html", "pdf"]

    if "--help" in argv or "--help-commands" in argv:
        process_standard_options_for_setup_help(argv)
        return True
    fLOG("[process_standard_options_for_setup]", argv)

    def process_argv_for_unittest(argv):
        if "-d" in argv:
            ld = argv.index("-d")
            if ld >= len(argv) - 1:
                raise ValueError(
                    "Option -d should be follow by a duration in seconds.")
            d = float(argv[ld + 1])
        else:
            d = None

        if "-f" in argv:
            lf = argv.index("-f")
            if lf >= len(argv) - 1:
                raise ValueError(
                    "Option -d should be follow by a duration in seconds.")
            f = argv[lf + 1]
        else:
            f = None

        if "-e" in argv:
            le = argv.index("-e")
            if le >= len(argv) - 1:
                raise ValueError(
                    "Option -e should be follow by a regular expression.")
            e = re.compile(argv[le + 1])
        else:
            e = None

        if "-g" in argv:
            lg = argv.index("-g")
            if lg >= len(argv) - 1:
                raise ValueError(
                    "Option -g should be follow by a regular expression.")
            g = re.compile(argv[lg + 1])
        else:
            g = None

        if f is None and d is None and e is None and g is None:
            return skip_function
        else:

            def ereg(name):
                return (e is None) or (e.search(name) is not None)

            def greg(name):
                return (g is None) or (g.search(name) is None)

            if f is not None:
                if d is not None:
                    raise NotImplementedError(
                        "Options -f and -d cannot be specified at the same time.")

                def allow(name, code, duration):
                    name = os.path.split(name)[-1]
                    return f not in name and ereg(name) and greg(name)
                return allow
            else:
                # d is not None
                def skip_allowd(name, code, duration):
                    name = os.path.split(name)[-1]
                    cond = (duration is None or d is None or duration <=
                            d) and ereg(name) and greg(name)
                    return not cond
                return skip_allowd

    folder = file_or_folder if os.path.isdir(
        file_or_folder) else os.path.dirname(file_or_folder)
    unit_test_folder = os.path.join(folder, "_unittests")
    fLOG("unittest_modules={0}".format(unittest_modules))

    if unittest_modules is None:
        unittest_modules_py3to2 = None
        unittest_modules_script = None
    else:
        unittest_modules_py3to2 = []
        unittest_modules_script = []
        for mod in unittest_modules:
            if isinstance(mod, tuple):
                unittest_modules_py3to2.append(mod[0])
                unittest_modules_script.append(mod[1])
            else:
                unittest_modules_py3to2.append(mod)
                unittest_modules_script.append(mod)

    # dump unit test coverage?

    def dump_coverage_fct(full=True):
        mn = project_var_name if module_name is None else module_name
        full_path = _get_dump_default_path(folder, mn, argv)
        if full_path is None or full:
            return full_path
        else:
            sub = os.path.split(full_path)[0]
            sub = os.path.split(sub)[0]
            return sub

    # starts interpreting the commands

    if "clean_space" in argv:
        rem = clean_space_for_setup(
            file_or_folder, file_filter=file_filter_pep8)
        print("[clean_space] number of impacted files (pep8 + rst):", len(rem))
        rem = clean_notebooks_for_numbers(file_or_folder)
        print("[clean_space] number of impacted notebooks:", len(rem))
        return True

    elif "write_version" in argv:
        fLOG("---- JENKINS BEGIN WRITE VERSION ----")
        write_version_for_setup(file_or_folder)
        fLOG("---- JENKINS BEGIN END VERSION ----")
        return True

    elif "clean_pyd" in argv:
        clean_space_for_setup(file_or_folder)
        return True

    elif "build_sphinx" in argv:
        if setup_params is None:
            setup_params = {}
        out, err = call_setup_hook(folder,
                                   project_var_name if module_name is None else module_name,
                                   fLOG=fLOG,
                                   **setup_params)
        if len(err) > 0 and err != "no _setup_hook":
            raise Exception(
                "unable to run _setup_hook\nOUT:\n{0}\n[setuperror]\n{1}".format(out, err))

        if func_sphinx_begin is not None:
            func_sphinx_begin(argv=argv, file_or_folder=file_or_folder, project_var_name=project_var_name,
                              module_name=module_name, unittest_modules=unittest_modules, pattern_copy=pattern_copy,
                              requirements=requirements, port=port, blog_list=blog_list, default_engine_paths=default_engine_paths,
                              extra_ext=extra_ext, add_htmlhelp=add_htmlhelp, setup_params=setup_params, coverage_options=coverage_options,
                              coverage_exclude_lines=coverage_exclude_lines, func_sphinx_begin=func_sphinx_begin, func_sphinx_end=func_sphinx_end,
                              additional_notebook_path=additional_notebook_path, nbformats=nbformats, layout=layout,
                              skip_function=skip_function, addition_ut_path=additional_ut_path, fLOG=fLOG)
        standard_help_for_setup(argv,
                                file_or_folder, project_var_name, module_name=module_name, extra_ext=extra_ext,
                                add_htmlhelp=add_htmlhelp, copy_add_ext=copy_add_ext, nbformats=nbformats, layout=layout,
                                use_run_cmd=use_run_cmd, fLOG=fLOG)

        if func_sphinx_end is not None:
            func_sphinx_end(argv=argv, file_or_folder=file_or_folder, project_var_name=project_var_name,
                            module_name=module_name, unittest_modules=unittest_modules, pattern_copy=pattern_copy,
                            requirements=requirements, port=port, blog_list=blog_list, default_engine_paths=default_engine_paths,
                            extra_ext=extra_ext, add_htmlhelp=add_htmlhelp, setup_params=setup_params, coverage_options=coverage_options,
                            coverage_exclude_lines=coverage_exclude_lines, func_sphinx_begin=func_sphinx_begin, func_sphinx_end=func_sphinx_end,
                            additional_notebook_path=additional_notebook_path, nbformats=nbformats, layout=layout,
                            skip_function=skip_function, addition_ut_path=additional_ut_path, fLOG=fLOG)

        return True

    elif "unittests" in argv:
        skip_f = process_argv_for_unittest(argv)
        run_unittests_for_setup(file_or_folder, setup_params=setup_params,
                                coverage_options=coverage_options,
                                coverage_exclude_lines=coverage_exclude_lines,
                                additional_ut_path=additional_ut_path,
                                skip_function=skip_f, covtoken=covtoken,
                                hook_print=hook_print, stdout=stdout, stderr=stderr,
                                filter_warning=filter_warning, dump_coverage=dump_coverage_fct(),
                                add_coverage_folder=dump_coverage_fct(False), fLOG=fLOG)
        return True

    elif "setup_hook" in argv:
        fLOG("---- JENKINS BEGIN SETUPHOOK ----")
        run_unittests_for_setup(
            file_or_folder, setup_params=setup_params, only_setup_hook=True,
            coverage_options=coverage_options, coverage_exclude_lines=coverage_exclude_lines,
            additional_ut_path=additional_ut_path, skip_function=skip_function,
            hook_print=hook_print, stdout=stdout, stderr=stderr, dump_coverage=dump_coverage_fct(),
            fLOG=fLOG)
        fLOG("---- JENKINS END SETUPHOOK ----")
        return True

    elif "unittests_LONG" in argv:
        def skip_long(name, code, duration):
            return "test_LONG_" not in name
        run_unittests_for_setup(
            file_or_folder, skip_function=skip_long, setup_params=setup_params,
            coverage_options=coverage_options, coverage_exclude_lines=coverage_exclude_lines,
            additional_ut_path=additional_ut_path, hook_print=hook_print,
            stdout=stdout, stderr=stderr, dump_coverage=dump_coverage_fct(),
            fLOG=fLOG)
        return True

    elif "unittests_SKIP" in argv:
        def skip_skip(name, code, duration):
            return "test_SKIP_" not in name
        run_unittests_for_setup(
            file_or_folder, skip_function=skip_skip, setup_params=setup_params,
            coverage_options=coverage_options, coverage_exclude_lines=coverage_exclude_lines,
            additional_ut_path=additional_ut_path, hook_print=hook_print,
            stdout=stdout, stderr=stderr, dump_coverage=dump_coverage_fct(),
            fLOG=fLOG)
        return True

    elif "unittests_GUI" in argv:
        def skip_skip(name, code, duration):
            return "test_GUI_" not in name
        run_unittests_for_setup(
            file_or_folder, skip_function=skip_skip, setup_params=setup_params,
            coverage_options=coverage_options, coverage_exclude_lines=coverage_exclude_lines,
            additional_ut_path=additional_ut_path, hook_print=hook_print,
            stdout=stdout, stderr=stderr, dump_coverage=dump_coverage_fct(),
            fLOG=fLOG)
        return True

    elif "build_script" in argv:

        # script running setup.py

        script = get_build_script(
            project_var_name, requirements=requirements, port=port,
            default_engine_paths=default_engine_paths)
        binto = os.path.join(folder, "bin")
        if not os.path.exists(binto):
            os.mkdir(binto)
        with open(os.path.join(folder, "bin", "auto_unittest_setup_help.%s" % get_script_extension()), "w") as f:
            f.write(script)

        for c in ("build_script", "clean_space",
                  "write_version", "clean_pyd",
                  "build_sphinx", "unittests",
                  "unittests_LONG", "unittests_SKIP", "unittests_GUI",
                  "unittests -d 5", "setup_hook", "copy27", "test_local_pypi"):
            sc = get_script_command(
                c, project_var_name, requirements=requirements, port=port, platform=sys.platform,
                default_engine_paths=default_engine_paths, additional_local_path=additional_local_path)
            cn = c.replace(" ", "_")
            with open(os.path.join(folder, "bin", "auto_setup_%s.%s" % (cn, get_script_extension())), "w") as f:
                f.write(sc)

        # script running for a developper

        for c in {"notebook", "publish", "publish_doc", "local_pypi", "run27",
                  "build27", "setupdep", "copy_dist",
                  "any_setup_command", "build_dist",
                  "copy_sphinx", "lab"}:
            if "--private" in argv and "publish" in c:
                # we skip this to avoid producing scripts for publish
                # functionalities
                continue
            sc = get_extra_script_command(c, project_var_name, requirements=requirements,
                                          port=port, platform=sys.platform,
                                          default_engine_paths=default_engine_paths,
                                          unit_test_folder=unit_test_folder,
                                          unittest_modules=unittest_modules_script,
                                          additional_notebook_path=additional_notebook_path,
                                          additional_local_path=additional_local_path)
            if sc is None:
                continue
            if c == "setupdep":
                folder_setup = os.path.join(folder, "build", "auto_setup")
                if not os.path.exists(folder_setup):
                    os.makedirs(folder_setup)
                with open(os.path.join(folder_setup, "auto_setup_dep.py"), "w") as f:
                    f.write(sc)
            else:
                with open(os.path.join(folder, "bin", "auto_cmd_%s.%s" % (c, get_script_extension())), "w") as f:
                    f.write(sc)

        # script for anybody
        write_module_scripts(
            folder, platform=sys.platform, blog_list=blog_list, default_engine_paths=default_engine_paths)

        # pyproj for PTVS
        if sys.platform.startswith("win"):
            write_pyproj(folder)

        return True

    elif "copy27" in argv:
        if sys.version_info[0] < 3:
            raise Exception("Python needs to be Python3")
        root = os.path.abspath(os.path.dirname(file_or_folder))
        root = os.path.normpath(root)
        dest = os.path.join(root, "dist_module27")
        py3to2_convert_tree(
            root, dest, unittest_modules=unittest_modules_py3to2, pattern_copy=pattern_copy)
        return True

    elif "test_local_pypi" in argv:
        url = "http://localhost:{0}/".format(port)
        content = get_url_content_timeout(url, timeout=5)
        if content is None or len(content) == 0:
            raise Exception("test failed for url: " + url)
        print(content)
        return True

    else:
        return False


def get_script_extension():
    """
    Returns the scripts extension based on the system it is running on.

    @return     bat or sh
    """
    if sys.platform.startswith("win"):
        return "bat"
    else:
        return "sh"


def get_folder(file_or_folder):
    """
    Returns the folder which contains ``setup.py``.

    @param      file_or_folder      file ``setup.py`` or folder which contains it
    @return                         folder
    """
    file_or_folder = os.path.abspath(file_or_folder)
    if os.path.isdir(file_or_folder):
        folder = file_or_folder
    else:
        folder = os.path.dirname(file_or_folder)
    return folder


def write_version_for_setup(file_or_folder):
    """
    Extracts the version number,
    the function writes the files ``version.txt`` in this folder.

    @param      file_or_folder      file ``setup.py`` or folder which contains it
    @return                         version number

    .. versionadded:: 1.1
    """
    src = SourceRepository(commandline=True)
    ffolder = get_folder(file_or_folder)
    version = src.version(ffolder)
    if version in ["0", 0, None]:
        raise Exception("issue with version {0}".format(version))

    # write version number
    if version is not None:
        with open(os.path.join(ffolder, "version.txt"), "w") as f:
            f.write(str(version) + "\n")

    return version


def clean_space_for_setup(file_or_folder, file_filter=None):
    """
    .. index:: pep8

    Does some cleaning within the module, apply :epkg:`pep8` rules.

    @param      file_or_folder      file ``setup.py`` or folder which contains it
    @param      file_filter         file filter (see @see fn remove_extra_spaces_folder)
    @return                         impacted files

    .. versionchanged:: 1.5
        Parameter *file_filter* was added.
    """
    ffolder = get_folder(file_or_folder)
    rem = remove_extra_spaces_folder(
        ffolder,
        extensions=[
            ".py",
            ".rst",
            ".md",
            ".bat",
            ".sh"],
        file_filter=file_filter)
    return rem


def clean_notebooks_for_numbers(file_or_folder):
    """
    Upgrades notebooks to the latest format and
    cleans notebooks execution numbers and rearranges the JSON file.

    @param      file_or_folder      file ``setup.py`` or folder which contains it
    @return                         impacted files

    .. index:: notebooks
    """
    ffolder = get_folder(file_or_folder)
    fold2 = os.path.normpath(
        os.path.join(ffolder, "_doc", "notebooks"))
    mod = []
    for nbf in explore_folder_iterfile(fold2, pattern=".*[.]ipynb"):
        t = upgrade_notebook(nbf)
        if t:
            mod.append(nbf)
        # remove numbers
        s = remove_execution_number(nbf, nbf)
        if s:
            mod.append(nbf)
    return mod


def standard_help_for_setup(argv, file_or_folder, project_var_name, module_name=None, extra_ext=None,
                            add_htmlhelp=False, copy_add_ext=None,
                            nbformats=("ipynb", "html", "python",
                                       "rst", "slides", "pdf", "present"),
                            layout=None,  # , "epub"],
                            use_run_cmd=False, fLOG=noLOG):
    """
    Standard function which generates help assuming they follow the same design
    as *pyquickhelper*.

    @param      argv                it should be ``sys.argv``
    @param      file_or_folder      file ``setup.py`` or folder which contains it
    @param      project_var_name    display name of the module
    @param      module_name         module name, None if equal to *project_var_name* (``import <module_name>``)
    @param      extra_ext           extra file extension to process (ex ``["doc"]``)
    @param      add_htmlhelp        run HTML Help too (only on Windows)
    @param      copy_add_ext        additional extension of files to copy
    @param      nbformats           notebooks format to generate
    @param      layout              layout for the documentation, if None --> ``["html", "pdf"]``
    @param      use_run_cmd         use function @see fn run_cmd instead of ``os.system``
                                    to build the documentation
    @param      fLOG                logging function

    The function outputs some information through function @see fn fLOG.

    A page will be added for each extra file extension mentioned in *extra_ext* if
    some of these were found.
    """
    if "--help" in argv:
        from ..helpgen.help_usage import get_help_usage
        print(get_help_usage())
    else:
        from ..helpgen.sphinx_main import generate_help_sphinx

        if layout is None:
            layout = ["html", "pdf"]
        if module_name is None:
            module_name = project_var_name

        ffolder = get_folder(file_or_folder)
        source = os.path.join(ffolder, "_doc", "sphinxdoc", "source")

        if not os.path.exists(source):
            raise FileNotFoundError(
                "you must get the source from GitHub to build the documentation,\nfolder {0} "
                "should exist\n(file_or_folder={1})\n(ffolder={2})\n(cwd={3})".format(source, file_or_folder, ffolder, os.getcwd()))

        if "conf" in sys.modules:
            warnings.warn("module conf was imported, this function expects not to:\n{0}".format(
                sys.modules["conf"].__file__))
            del sys.modules["conf"]

        project_name = os.path.split(
            os.path.split(os.path.abspath(ffolder))[0])[-1]

        generate_help_sphinx(project_name, module_name=module_name, layout=layout,
                             extra_ext=extra_ext, nbformats=nbformats, add_htmlhelp=add_htmlhelp,
                             copy_add_ext=copy_add_ext, fLOG=fLOG, root=ffolder)


def run_unittests_for_setup(file_or_folder, skip_function=default_skip_function, setup_params=None,
                            only_setup_hook=False, coverage_options=None, coverage_exclude_lines=None,
                            additional_ut_path=None, covtoken=None, hook_print=True, stdout=None,
                            stderr=None, filter_warning=None, dump_coverage=None,
                            add_coverage_folder=None, fLOG=noLOG):
    """
    Runs the unit tests and computes the coverage, stores
    the results in ``_doc/sphinxdoc/source/coverage``
    assuming the module follows the same design as *pyquickhelper*.

    @param      file_or_folder          file ``setup.py`` or folder which contains it
    @param      skip_function           see @see fn main_wrapper_tests
    @param      setup_params            see @see fn main_wrapper_tests
    @param      only_setup_hook         see @see fn main_wrapper_tests
    @param      coverage_options        see @see fn main_wrapper_tests
    @param      coverage_exclude_lines  see @see fn main_wrapper_tests
    @param      additional_ut_path      see @see fn main_wrapper_tests
    @param      covtoken                see @see fn main_wrapper_tests
    @param      hook_print              see @see fn main_wrapper_tests
    @param      stdout                  see @see fn main_wrapper_tests
    @param      stderr                  see @see fn main_wrapper_tests
    @param      filter_warning          see @see fn main_wrapper_tests
    @param      dump_coverage           location where to dump the coverage
    @param      add_coverage_folder     additional folder where to look for other coverage reports
    @param      fLOG                    logging function

    .. versionchanged:: 1.3
        Parameters *coverage_options*, *coverage_exclude_lines*, *fLOG*,
        *additional_ut_path*, *hook_print*, *stdout*, *stderr* were added.
        See function @see fn main_wrapper_tests.
        The coverage computation can be disable by specifying
        ``coverage_options["disable_coverage"] = True``.

        Parameter *covtoken* as added to post the coverage report to
        `codecov <https://codecov.io/>`_.

    .. versionchanged:: 1.4
        Parameter *filter_warning* was added.

    .. versionchanged:: 1.5
        Parameter *dump_coverage* was added.
        Dumps the unit test coverage in another location.

    .. versionchanged:: 1.6
        Parameter *add_coverage_folder* was added.
    """
    ffolder = get_folder(file_or_folder)
    funit = os.path.join(ffolder, "_unittests")
    if not os.path.exists(funit):
        raise FileNotFoundError(
            "You must get the whole source to run the unittests,\nfolder {0} should exist".format(funit))

    run_unit = os.path.join(funit, "run_unittests.py")
    if not os.path.exists(run_unit):
        content = os.listdir(funit)
        raise FileNotFoundError(
            "the folder {0} should contain run_unittests.py\nCONTENT:\n{1}".format(funit, "\n".join(content)))

    fix_tkinter_issues_virtualenv(fLOG=fLOG)

    cov = True
    if coverage_options:
        if "disable_coverage" in coverage_options and coverage_options["disable_coverage"]:
            cov = False

    if dump_coverage is not None and not cov:
        dump_coverage = None

    main_wrapper_tests(
        run_unit, add_coverage=cov, skip_function=skip_function, setup_params=setup_params,
        only_setup_hook=only_setup_hook, coverage_options=coverage_options,
        coverage_exclude_lines=coverage_exclude_lines, additional_ut_path=additional_ut_path,
        covtoken=covtoken, hook_print=hook_print, stdout=stdout, stderr=stderr,
        filter_warning=filter_warning, dump_coverage=dump_coverage,
        add_coverage_folder=add_coverage_folder, fLOG=fLOG)


def copy27_for_setup(file_or_folder):
    """
    prepare a copy of the source for Python 2.7,
    assuming the module follows the same design as *pyquickhelper*

    @param      file_or_folder      file ``setup.py`` or folder which contains it
    """
    if sys.version_info[0] < 3:
        raise Exception("Python needs to be Python3")

    root = get_folder(file_or_folder)
    root = os.path.normpath(root)
    dest = os.path.join(root, "dist_module27")
    py3to2_convert_tree(root, dest)


def write_pyproj(file_or_folder, location=None):
    """
    create a pyproj project to work with `PTVS <https://pytools.codeplex.com/>`_
    (Python Tools for Visual Studio)

    @param      file_or_folder      file ``setup.py`` or folder which contains it
    @param      location            if not None, stores the project into this folder

    This functionality fails with Python 2.7 (encoding).
    """
    avoid = ["dist", "build", "dist_module27",
             "_doc", "_virtualenv", "_virtualenv27", "_venv"]

    def filter(name):
        if os.path.splitext(name)[-1] != ".py":
            return False
        if "temp_" in name:
            return False
        for a in avoid:
            if name.startswith(a + "\\"):
                return False
            if name.startswith(a + "/"):
                return False
        return True

    root = get_folder(file_or_folder)
    root = os.path.normpath(root)
    name = os.path.split(root)[-1]
    if location is None:
        dest = os.path.join(root, "ptvs_project.pyproj")
    else:
        dest = os.path.join(location, "ptvs_project.pyproj")
    all_files = [os.path.relpath(_, root)
                 for _ in explore_folder_iterfile(root)]
    all_files = [_ for _ in all_files if filter(_)]
    pyproj = get_pyproj_project(name, all_files)
    with open(dest, "w", encoding="utf8") as f:
        f.write(pyproj.strip())


def process_standard_options_for_setup_help(argv):
    """
    print the added options available through this module
    """
    commands = {
        "build_script": "produce various scripts to build the module",
        "build_sphinx": "build the documentation",
        "build_wheel": "build the wheel",
        "build27": "build the wheel for Python 2.7 (if available), it requires to run copy27 first",
        "clean_space": "clean unnecessary spaces in the code, applies flake8 on all files",
        "clean_pyd": "clean file ``*.pyd``",
        "copy_dist": "copy documentation to folder dist",
        "copy_sphinx": "modify and copy sources to _doc/sphinxdoc/source/<module>",
        "copy27": "create a modified copy of the module to run on Python 2.7 (if available), it requires to run copy27 first",
        "run27": "run the unit tests for the Python 2.7",
        "setup_hook": "call function setup_hook which initializes the module before running unit tests",
        "unittests": "run the unit tests which do not contain test_LONG, test_SKIP or test_GUI in their file name",
        "unittests_LONG": "run the unit tests which contain test_LONG their file name",
        "unittests_SKIP": "run the unit tests which contain test_SKIP their file name",
        "unittests_GUI": "run the unit tests which contain test_GUI their file name",
        "write_version": "write a file ``version.txt`` with the version number (assuming sources are host with git)",
    }

    if "--help-commands" in argv:
        print("Commands processed by pyquickhelper:")
        for k, v in sorted(commands.items()):
            print("  {0}{1}{2}".format(
                k, " " * (len("copy27            ") - len(k)), v))
        print()
    elif "--help" in argv:
        docu = 0
        for k, v in sorted(commands.items()):
            if k in argv:
                docu += 1

        if docu == 0:
            print("pyquickhelper commands:")
            print()
            for k in sorted(commands):
                process_standard_options_for_setup_help(['--help', k])
            print()
        else:
            for k, v in sorted(commands.items()):
                if k in argv:
                    docu += 1
                    print("  setup.py {0}{1}{2}".format(
                        k, " " * (20 - len(k)), v))
                    if k == "unittests":
                        print(
                            "\n      {0} [-d seconds] [-f file] [-e regex] [-g regex]\n\n      {1}".format(k, v))
                        print(
                            "      -d seconds     run all unit tests for which predicted duration is below a given threshold.")
                        print(
                            "      -f file        run all unit tests in file (do not use the full path)")
                        print(
                            "      -e regex       run all unit tests files matching the regular expression")
                        print(
                            "      -g regex       run all unit tests files not matching the regular expression")
                        print()


def write_module_scripts(folder, platform=sys.platform, blog_list=None,
                         default_engine_paths=None, command=None):
    """
    Writes a couple of script which allow a user to be faster on some tasks
    or to easily get information about the module.

    @param      folder                  where to write the script
    @param      platform                platform
    @param      blog_list               blog list to follow, should be attribute ``__blog__`` of the module
    @param      command                 None to generate scripts for all commands or a value in *[blog, doc]*.
    @param      default_engine_paths    default engines (or python distributions)
    @return                             list of written scripts

    The function produces the following files:

    * *auto_rss_list.xml*: list of rss stream to follow
    * *auto_rss_database.db3*: stores blog posts
    * *auto_rss_server.py*: runs a server which updates the scripts and runs a server. It also open the default browser.
    * *auto_rss_server.(bat|sh)*: run *auto_run_server.py*, the file on Linux might be missing if there is an equivalent python script

    .. faqref::
        :title: How to generate auto_rss_server.py?

        The following code generates the script *auto_rss_local.py*
        which runs a local server to read blog posts included
        in the documentation (it uses module
        `pyrsslocal <http://www.xavierdupre.fr/app/pyrsslocal/helpsphinx/index.html>`_)::

            from pyquickhelper.pycode import write_module_scripts, __blog__
            write_module_scripts(".", blog_list=__blog__, command="blog")
    """
    default_set = {"blog", "doc"}
    if command is not None:
        if command not in default_set:
            raise ValueError(
                "command {0} is not available in {1}".format(command, default_set))
        commands = {command}
    else:
        commands = default_set

    res = []
    for c in commands:
        sc = get_script_module(
            c, platform=sys.platform, blog_list=blog_list, default_engine_paths=default_engine_paths)
        if sc is None:
            continue
        tobin = os.path.join(folder, "bin")
        if not os.path.exists(tobin):
            os.mkdir(tobin)
        for item in sc:
            if isinstance(item, tuple):
                name = os.path.join(folder, "bin", item[0])
                with open(name, "w", encoding="utf8") as f:
                    f.write(item[1])
                res.append(name)
            else:
                name = os.path.join(
                    folder, "bin", "auto_run_%s.%s" % (c, get_script_extension()))
                with open(name, "w") as f:
                    f.write(item)
                res.append(name)
    return res


def _get_dump_default_path(location, module_name, argv):
    """
    Proposes a default location to dump results about unit tests execution.

    @param      location    location of the module
    @param      module_name module name
    @param      argv        argument on the command line
    @return                 location of the dump

    The result is None for remote continuous integration.

    .. versionadded:: 1.5
    """
    from . import is_travis_or_appveyor
    if is_travis_or_appveyor():
        return None
    hash = hash_list(argv)
    setup = os.path.join(location, "setup.py")
    if not os.path.exists(setup):
        raise FileNotFoundError(setup)
    fold = os.path.join(location, "..", "_coverage_dumps")
    if not os.path.exists(fold):
        os.mkdir(fold)
    dt = datetime.datetime.now().strftime("%Y%m%dT%H%M")
    if module_name is None:
        raise ValueError("module_name cannot be None")
    dump = os.path.join(fold, module_name, hash, dt)
    if not os.path.exists(dump):
        os.makedirs(dump)
    return dump


def hash_list(argv, size=8):
    """
    Proposes a hash for the list of arguments.

    @param      argv        list of arguments on the command line.
    @param      size        size of the hash
    @return     string
    """
    st = "--".join(map(str, argv))
    hash = hashlib.md5()
    hash.update(st.encode("utf-8"))
    res = hash.hexdigest()
    if len(res) > 8:
        return res[:8]
    else:
        return res
