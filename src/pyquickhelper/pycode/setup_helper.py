"""
@file
@brief  Helper for the setup

.. versionadded:: 1.1
"""

import os
import sys
from ..loghelper.pyrepo_helper import SourceRepository
from ..loghelper.flog import noLOG
from ..helpgen.sphinx_main import generate_help_sphinx
from .code_helper import remove_extra_spaces_folder
from .py3to2 import py3to2_convert_tree
from ..pycode.utils_tests import main_wrapper_tests, default_skip_function
from ..helpgen import get_help_usage
from .build_helper import get_build_script, get_script_command, get_extra_script_command, get_script_module, get_pyproj_project
from ..filehelper import get_url_content_timeout, explore_folder_iterfile
from .call_setup_hook import call_setup_hook
from .tkinter_helper import fix_tkinter_issues_virtualenv

if sys.version_info[0] == 2:
    from codecs import open


def process_standard_options_for_setup(argv,
                                       file_or_folder,
                                       project_var_name,
                                       module_name=None,
                                       unittest_modules=None,
                                       pattern_copy=".*[.]((ico)|(dll)|(rst)|(ipynb)|(png)|(txt)|(zip)|(gz)|(html)|(exe)|(js)|(css))$",
                                       requirements=None,
                                       port=8067,
                                       blog_list=None,
                                       default_engine_paths=None,
                                       extra_ext=None,
                                       add_htmlhelp=False,
                                       setup_params=None,
                                       coverage_options=None,
                                       coverage_exclude_lines=None,
                                       func_sphinx_begin=None,
                                       func_sphinx_end=None,
                                       additional_notebook_path=None,
                                       additional_local_path=None,
                                       copy_add_ext=None,
                                       nbformats=[
                                           "ipynb", "html", "python", "rst", "slides", "pdf"],
                                       layout=["html", "pdf", "epub"],
                                       additional_ut_path=None,
                                       skip_function=default_skip_function,
                                       covtoken=None,
                                       hook_print=True,
                                       stdout=None,
                                       stderr=None,
                                       fLOG=noLOG):
    """
    process the standard options the module pyquickhelper is
    able to process assuming the module which calls this function
    follows the same design as *pyquickhelper*, it will process the following
    options:
        * ``build_script``: produce various scripts to build the module
        * ``build_sphinx``: build the documentation
        * ``clean_pyd``: clean file ``*.pyd``
        * ``clean_space``: clean unnecessary spaces in the code
        * ``copy27``: create a modified copy of the module to run on Python 2.7
        * ``test_local_pypi``: test a local pypi server
        * ``unittests``: run the unit tests except those beginning by ``test_SKIP_`` or ``test_LONG_``.
        * ``unittests_LONG``: run the unit tests beginning by ``test_LONG_``
        * ``unittests_SKIP``: run the unit tests beginning by ``test_SKIP_``
        * ``unittests_GUI``: run the unit tests beginning by ``test_GUI_``
        * ``write_version``: write a file ``version.txt`` with the version number (needs an access to GitHub)

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
                                            it is a list of tuple (layout, build directory, parameters to override)
    @param      additional_ut_path          additional paths to add when running unit tests
    @param      skip_function               function to skip unit tests, see @ee fn main_wrapper_tests
    @param      covtoken                    token used when publishing coverage report to `codecov <https://codecov.io/>`_,
                                            more in @see fn main_wrapper_tests
    @param      fLOG                        logging function
    @param      hook_print                  enable, disable print when calling *_setup_hook*
    @paral      stdout                      redirect stdout for unit test if not None
    @paral      stderr                      redirect stderr for unit test  if not None
    @return                                 True (an option was processed) or False,
                                            the file ``setup.py`` should call function ``setup``

    The command ``build_script`` is used, the flag ``--private`` can be used to
    avoid producing scripts to publish the module on `Pypi <https://pypi.python.org/pypi>`_.

    An example for *default_engine_paths*::

        default_engine_paths = {
            "windows": {
                "__PY34__": None,
                "__PY35__": None,
                "__PY35_X64__": "c:\\Python35_x64",
                "__PY34_X64__": "c:\\Python34_x64",
                "__PY27_X64__": "c:\\Anaconda2",
            },
        }

    .. versionchanged:: 1.3
        Parameters *coverage_options*, *coverage_exclude_lines*, *copy_add_ext* were added.
        See function @see fn main_wrapper_tests.

        Parameter *unittest_modules* now accepts a list of string and 2-uple.
        If it is a 2-uple, the first string is used to convert Python 3 code into Python 2
        (in case the local folder is different from the module name),
        the second string is used to add local path to the variable ``PYTHON_PATH``.
        If it is a single string, it means both name strings are equal.
        Parameters *func_sphinx_begin* and *func_sphinx_end* were added
        to pre-process or post-process the documentation.
        Parameter *additional_notebook_path* was added to specify some additional
        paths when preparing the script *auto_cmd_notebook.bat*.

        Parameters *layout*, *nbformats* were added.
        See function @see fn generate_help_sphinx.

        Parameters *fLOG*, *additional_ut_path*, *skip_function* were added.
        The coverage computation can be disable by specifying
        ``coverage_options["disable_coverage"] = True``.

        Parameter *covtoken* as added to post the coverage report to
        `codecov <https://codecov.io/>`_.

        Parameters *hook_print*, *stdout*, *stderr* were added.
    """
    folder = file_or_folder if os.path.isdir(
        file_or_folder) else os.path.dirname(file_or_folder)
    unit_test_folder = os.path.join(folder, "_unittests")

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

    if "clean_space" in argv:
        rem = clean_space_for_setup(file_or_folder)
        print("number of impacted files", len(rem))
        return True

    elif "write_version" in argv:
        write_version_for_setup(file_or_folder)
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
                "unable to run _setup_hook\nOUT:\n{0}\nERR:\n{1}".format(out, err))

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
                                fLOG=fLOG)

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
        run_unittests_for_setup(file_or_folder, setup_params=setup_params,
                                coverage_options=coverage_options,
                                coverage_exclude_lines=coverage_exclude_lines,
                                additional_ut_path=additional_ut_path,
                                skip_function=skip_function, covtoken=covtoken,
                                hook_print=hook_print, stdout=stdout, stderr=stderr,
                                fLOG=fLOG)
        return True

    elif "setup_hook" in argv:
        run_unittests_for_setup(
            file_or_folder, setup_params=setup_params, only_setup_hook=True,
            coverage_options=coverage_options, coverage_exclude_lines=coverage_exclude_lines,
            additional_ut_path=additional_ut_path, skip_function=skip_function,
            hook_print=hook_print, stdout=stdout, stderr=stderr, fLOG=fLOG)
        return True

    elif "unittests_LONG" in argv:
        def skip_long(name, code):
            return "test_LONG_" not in name
        run_unittests_for_setup(
            file_or_folder, skip_function=skip_long, setup_params=setup_params,
            coverage_options=coverage_options, coverage_exclude_lines=coverage_exclude_lines,
            additional_ut_path=additional_ut_path, hook_print=hook_print,
            stdout=stdout, stderr=stderr, fLOG=fLOG)
        return True

    elif "unittests_SKIP" in sys.argv:
        def skip_skip(name, code):
            return "test_SKIP_" not in name
        run_unittests_for_setup(
            file_or_folder, skip_function=skip_skip, setup_params=setup_params,
            coverage_options=coverage_options, coverage_exclude_lines=coverage_exclude_lines,
            additional_ut_path=additional_ut_path, hook_print=hook_print,
            stdout=stdout, stderr=stderr, fLOG=fLOG)
        return True

    elif "unittests_GUI" in sys.argv:
        def skip_skip(name, code):
            return "test_GUI_" not in name
        run_unittests_for_setup(
            file_or_folder, skip_function=skip_skip, setup_params=setup_params,
            coverage_options=coverage_options, coverage_exclude_lines=coverage_exclude_lines,
            additional_ut_path=additional_ut_path, hook_print=hook_print,
            stdout=stdout, stderr=stderr, fLOG=fLOG)
        return True

    elif "build_script" in argv:

        # script running setup.py

        script = get_build_script(
            project_var_name, requirements=requirements, port=port,
            default_engine_paths=default_engine_paths)
        with open(os.path.join(folder, "auto_unittest_setup_help.%s" % get_script_extension()), "w") as f:
            f.write(script)

        for c in {"build_script", "clean_space",
                  "write_version", "clean_pyd",
                  "build_sphinx", "unittests",
                  "unittests_LONG", "unittests_SKIP", "unittests_GUI",
                  "setup_hook", "copy27", "test_local_pypi"}:
            sc = get_script_command(
                c, project_var_name, requirements=requirements, port=port, platform=sys.platform,
                default_engine_paths=default_engine_paths, additional_local_path=additional_local_path)
            with open(os.path.join(folder, "auto_setup_%s.%s" % (c, get_script_extension())), "w") as f:
                f.write(sc)

        # script running for a developper

        for c in {"notebook", "publish", "publish_doc", "local_pypi", "run27",
                  "build27", "setupdep", "copy_dist",
                  "any_setup_command", "build_dist",
                  "copy_sphinx"}:
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
                with open(os.path.join(folder, "auto_cmd_%s.%s" % (c, get_script_extension())), "w") as f:
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
    returns the scripts extension based on the system it is running on

    @return     bat or sh
    """
    if sys.platform.startswith("win"):
        return "bat"
    else:
        return "sh"


def get_folder(file_or_folder):
    """
    returns the folder which contains ``setup.py``

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
    extract the version number,
    the function writes the files ``version.txt`` in this folder

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


def clean_space_for_setup(file_or_folder):
    """
    .. index:: pep8

    does some cleaning within the module, apply pep8 rules

    @param      file_or_folder      file ``setup.py`` or folder which contains it
    @return                         deleted files
    """
    ffolder = get_folder(file_or_folder)
    rem = remove_extra_spaces_folder(
        ffolder,
        extensions=[
            ".py",
            "rst",
            ".bat",
            ".sh"])
    return rem


def standard_help_for_setup(argv, file_or_folder, project_var_name, module_name=None, extra_ext=None,
                            add_htmlhelp=False, copy_add_ext=None,
                            nbformats=["ipynb", "html", "python",
                                       "rst", "slides", "pdf"],
                            layout=["html", "pdf", "epub"], fLOG=noLOG):
    """
    standard function to generate help assuming they follow the same design
    as *pyquickhelper*

    @param      argv                it should be ``sys.argv``
    @param      file_or_folder      file ``setup.py`` or folder which contains it
    @param      project_var_name    display name of the module
    @param      module_name         module name, None if equal to *project_var_name* (``import <module_name>``)
    @param      extra_ext           extra file extension to process (ex ``["doc"]``)
    @param      add_htmlhelp        run HTML Help too (only on Windows)
    @param      copy_add_ext        additional extension of files to copy
    @param      nbformats           notebooks format to generate
    @param      layout              layout for the documentation
    @param      fLOG                logging function

    The function outputs some information through function @see fn fLOG.

    A page will be added for each extra file extension mentioned in *extra_ext* if
    some of these were found.

    .. versionchanged:: 1.3
        Parameter *copy_add_ext*, *nbformats*, *argv* were added.
    """
    if "--help" in argv:
        print(get_help_usage())
    else:
        if module_name is None:
            module_name = project_var_name

        ffolder = get_folder(file_or_folder)
        source = os.path.join(ffolder, "_doc", "sphinxdoc", "source")

        if not os.path.exists(source):
            raise FileNotFoundError(
                "you must get the source from GitHub to build the documentation,\nfolder {0} "
                "should exist\n(file_or_folder={1})\n(ffolder={2})\n(cwd={3})".format(source, file_or_folder, ffolder, os.getcwd()))

        if "conf" in sys.modules:
            raise ImportError("module conf was imported, this function expects not to:\n{0}".format(
                sys.modules["conf"].__file__))

        project_name = os.path.split(
            os.path.split(os.path.abspath(ffolder))[0])[-1]

        generate_help_sphinx(project_name,
                             module_name=module_name,
                             layout=layout,
                             extra_ext=extra_ext,
                             nbformats=nbformats,
                             add_htmlhelp=add_htmlhelp,
                             copy_add_ext=copy_add_ext,
                             fLOG=fLOG)


def run_unittests_for_setup(file_or_folder,
                            skip_function=default_skip_function,
                            setup_params=None,
                            only_setup_hook=False,
                            coverage_options=None,
                            coverage_exclude_lines=None,
                            additional_ut_path=None,
                            covtoken=None,
                            hook_print=True,
                            stdout=None,
                            stderr=None,
                            fLOG=noLOG):
    """
    run the unit tests and compute the coverage, stores
    the results in ``_doc/sphinxdoc/source/coverage``
    assuming the module follows the same design as *pyquickhelper*

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
    @param      fLOG                    logging function

    .. versionchanged:: 1.3
        Parameters *coverage_options*, *coverage_exclude_lines*, *fLOG*,
        *additional_ut_path*, *hook_print*, *stdout*, *stderr* were added.
        See function @see fn main_wrapper_tests.
        The coverage computation can be disable by specifying
        ``coverage_options["disable_coverage"] = True``.

        Parameter *covtoken* as added to post the coverage report to
        `codecov <https://codecov.io/>`_.
    """
    ffolder = get_folder(file_or_folder)
    funit = os.path.join(ffolder, "_unittests")
    if not os.path.exists(funit):
        raise FileNotFoundError(
            "you must get the source from GitHub to run the unittests,\nfolder {0} should exist".format(funit))

    run_unit = os.path.join(funit, "run_unittests.py")
    if not os.path.exists(run_unit):
        content = os.listdir(funit)
        raise FileNotFoundError(
            "the folder {0} should contain run_unittests.py\nCONTENT:\n{1}".format(funit, "\n".join(content)))

    fix_tkinter_issues_virtualenv()

    cov = True
    if coverage_options:
        if "disable_coverage" in coverage_options and coverage_options["disable_coverage"]:
            cov = False

    main_wrapper_tests(
        run_unit, add_coverage=cov, skip_function=skip_function, setup_params=setup_params,
        only_setup_hook=only_setup_hook, coverage_options=coverage_options,
        coverage_exclude_lines=coverage_exclude_lines, additional_ut_path=additional_ut_path,
        covtoken=covtoken, hook_print=hook_print, stdout=stdout, stderr=stderr, fLOG=fLOG)


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
             "_doc", "_virtualenv", "_virtualenv27"]

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


def process_standard_options_for_setup_help():
    """
    print the added options available through this module
    """
    print("""
        Help for options added by pyquickhelper:

        build_script    produce various scripts to build the module
        clean_space     clean unnecessary spaces in the code
        write_version   write a file ``version.txt`` with the version number (needs an access to GitHub)
        clean_pyd       clean file ``*.pyd``
        build_sphinx    build the documentation
        unittests       run the unit tests
        copy27          create a modified copy of the module to run on Python 2.7

        """)


def write_module_scripts(folder, platform=sys.platform, blog_list=None,
                         default_engine_paths=None, command=None):
    """
    Writes a couple of script which allow a user to be faster on some tasks
    or to easily get information about the module.

    @param      folder      where to write the script
    @param      platform    platform
    @param      blog_list   blog list to follow, should be attribute ``__blog__`` of the module
    @param      command     None to generate scripts for all commands or a value in *[blog, doc]*.
    @return                 list of written scripts

    The function produces the following files:

    * *auto_rss_list.xml*: list of rss stream to follow
    * *auto_rss_database.db3*: stores blog posts
    * *auto_rss_server.py*: runs a server which updates the scripts and runs a server. It also open the default browser.
    * *auto_rss_server.(bat|sh)*: run *auto_run_server.py*, the file on Linux might be missing if there is an equivalent python script

    @example(How to generate auto_rss_server.py)
    The following code generates the script *auto_rss_local.py*
    which runs a local server to read blog posts included
    in the documentation (it uses module
    `pyrsslocal <http://www.xavierdupre.fr/app/pyrsslocal/helpsphinx/index.html>`_)::

        from pyquickhelper import write_module_scripts, __blog__
        write_module_scripts(".", blog_list=__blog__, command="blog")

    @endexample
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
        for item in sc:
            if isinstance(item, tuple):
                name = os.path.join(folder, item[0])
                with open(name, "w", encoding="utf8") as f:
                    f.write(item[1])
                res.append(name)
            else:
                name = os.path.join(
                    folder, "auto_run_%s.%s" % (c, get_script_extension()))
                with open(name, "w") as f:
                    f.write(item)
                res.append(name)
    return res
