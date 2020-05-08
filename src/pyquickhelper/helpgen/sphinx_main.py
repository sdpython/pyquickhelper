# -*- coding: utf-8 -*-
"""
@file
@brief Contains the main function to generate the documentation
for a module designed the same way as this one, @see fn generate_help_sphinx.
"""
import os
import sys
import shutil
import warnings
from datetime import datetime
from io import StringIO
from docutils.parsers.rst import directives, roles
from sphinx.cmd.build import main as build_main
from ..filehelper import remove_folder
from ..loghelper import python_path_append
from ..loghelper.process_script import execute_script_get_local_variables, dictionary_as_class
from ..loghelper.flog import run_cmd, fLOG
from .utils_sphinx_doc import prepare_file_for_sphinx_help_generation
from .utils_sphinx_doc_helpers import HelpGenException, ImportErrorHelpGen
from .conf_path_tools import find_latex_path, find_pandoc_path
from ..filehelper.synchelper import explore_folder
from ..filehelper import synchronize_folder
from .post_process import post_process_latex_output
from .process_notebooks import process_notebooks, build_notebooks_gallery, build_all_notebooks_coverage
from .sphinx_helper import post_process_html_nb_output_static_file
from .install_js_dep import install_javascript_tools
from .sphinx_main_helper import setup_environment_for_help, get_executables_path, generate_changes_repo
from .sphinx_main_helper import compile_latex_output_final, replace_placeholder_by_recent_blogpost
from .sphinx_main_helper import format_history, enumerate_copy_images_for_slides
from .sphinx_main_verification import verification_html_format
from .sphinx_main_missing_html_files import add_missing_files
from .style_css_template import style_figure_notebook
from .post_process_custom import find_custom_latex_processing
from ..sphinxext.blog_post_list import BlogPostList
from ..sphinxext.sphinx_blog_extension import BlogPostDirective, BlogPostDirectiveAgg
from ..sphinxext.sphinx_runpython_extension import RunPythonDirective
from ..sphinxext.sphinx_postcontents_extension import PostContentsDirective
from ..sphinxext.sphinx_tocdelay_extension import TocDelayDirective
from ..sphinxext.sphinx_youtube_extension import YoutubeDirective
from ..sphinxext.sphinx_sharenet_extension import ShareNetDirective, sharenet_role
from ..sphinxext.sphinx_downloadlink_extension import process_downloadlink_role
from ..sphinxext.sphinx_video_extension import VideoDirective
from ..sphinxext.sphinx_image_extension import SimpleImageDirective
from ..sphinxext.sphinximages.sphinxtrib.images import ImageDirective
from ..sphinxext.sphinx_template_extension import tpl_role
from ..sphinxext.sphinx_epkg_extension import epkg_role
from ..sphinxext.sphinx_bigger_extension import bigger_role
from ..sphinxext.sphinx_githublink_extension import githublink_role
from ..sphinxext.sphinx_gitlog_extension import gitlog_role
from ..sphinxext.sphinx_mathdef_extension import MathDef
from ..sphinxext.sphinx_quote_extension import QuoteNode
from ..sphinxext.sphinx_blocref_extension import BlocRef
from ..sphinxext.sphinx_exref_extension import ExRef
from ..sphinxext.sphinx_faqref_extension import FaqRef
from ..sphinxext.sphinx_nbref_extension import NbRef
from ..sphinxext.sphinx_cmdref_extension import CmdRef
from ..sphinxext.sphinx_todoext_extension import TodoExt
from ..sphinxext.sphinx_collapse_extension import CollapseDirective
from ..sphinxext.sphinx_gdot_extension import GDotDirective

template_examples = """

List of programs
++++++++++++++++

.. toctree::
   :maxdepth: 2

.. autosummary:: __init__.py
   :toctree: %s/
   :template: modules.rst

Another list
++++++++++++

"""


def generate_help_sphinx(project_var_name, clean=False, root=".",
                         filter_commit=lambda c: c.strip() != "documentation",
                         extra_ext=None,
                         nbformats=("ipynb", "slides", "html", "python",
                                    "rst", "pdf", "github"),
                         layout=None,
                         module_name=None, from_repo=True, add_htmlhelp=False,
                         copy_add_ext=None, direct_call=False, fLOG=fLOG,
                         parallel=1, extra_paths=None, fexclude=None):
    """
    Runs the help generation:

    - copies every file in another folder,
    - replaces comments in doxygen format into rst format,
    - replaces local import by global import (tweaking sys.path too),
    - calls sphinx to generate the documentation.

    @param      project_var_name    project name
    @param      clean               if True, cleans the previous documentation first
                                    (:epkg:`html` files)
    @param      root                see below
    @param      filter_commit       function which accepts a commit to show on the documentation
                                    (based on the comment)
    @param      extra_ext           list of file extensions to document (not .py)
    @param      nbformats           requested formats for the notebooks conversion
    @param      layout              list of formats sphinx should generate such as html, latex, pdf, docx,
                                    it is a list of tuple (layout, build directory, parameters to override),
                                    if None --> ``[("html", "build", {})]``
    @param      module_name         name of the module (must be the folder name ``src/module_name``
                                    if None, ``module_name``
                                    will be replaced by *project_var_name*
    @param      from_repo           if True, assumes the sources come from a source repository,
                                    False otherwise
    @param      add_htmlhelp        run :epkg:`HTML` Help too (only on :epkg:`Windows`)
    @param      copy_add_ext        additional file extension to copy
    @param      direct_call         direct call to sphinx with *sphinx_build* if *True*
                                    or run a command line in an another process to get
                                    a clear environment
    @param      parallel            degree of parallelization
    @param      extra_paths         extra paths when importing configuration
    @param      fexclude            function which tells which file not to copy in the folder
                                    used to build the documentation
    @param      fLOG                logging function

    The result is stored in path: ``root/_doc/sphinxdoc/source``.
    We assume the file ``root/_doc/sphinxdoc/source/conf.py`` exists
    as well as ``root/_doc/sphinxdoc/source/index.rst``.

    If you generate latex/pdf files, you should add variables ``latex_path`` and ``pandoc_path``
    in your file ``conf.py`` which defines the help.

    You can exclud some part while generating the documentation by adding:

    * ``# -- HELP BEGIN EXCLUDE --``
    * ``# -- HELP END EXCLUDE --``

    ::

        latex_path  = r"C:/Program Files/MiKTeX 2.9/miktex/bin/x64"
        pandoc_path = r"%USERPROFILE%/AppData/Local/Pandoc"

    .. exref::
        :title: Run help generation
        :index: extension, extra extension, ext

        ::

            # from the main folder which contains folder src or the sources
            generate_help_sphinx("pyquickhelper")

    By default, the function only consider files end by ``.py`` and ``.rst`` but you could
    add other files sharing the same extensions by adding this one
    in the ``extra_ext`` list.

    The function requires:

    - :epkg:`pandoc`
    - latex

    @warning Some themes such as `Bootstrap Sphinx Theme <http://ryan-roemer.github.io/sphinx-bootstrap-theme/>`_
        do not work on Internet Explorer. In that case, the
        file ``<python_path>/Lib/site-packages/sphinx/themes/basic/layout.html``
        must be modified to add the following line (just below ``Content-Type``).

        ::

            <meta http-equiv="X-UA-Compatible" content="IE=edge" />

    .. index:: PEP8, autopep8

    The code should follow as much as possible the sytle convention
    `PEP8 <https://www.python.org/dev/peps/pep-0008/>`_.
    The module `autopep8 <https://pypi.python.org/pypi/autopep8>`_ can modify a file or all files contained in one folder
    by running the following command line:

    ::

        autopep8 <folder> --recursive --in-place --pep8-passes 2000 --verbose

    **About encoding:** utf-8 without BOM is the recommanded option.

    **About languages:** only one language can be specificied even if you have
        multiple configuration file. Only the language specified in the main
        ``conf.py`` will be considered.

    **About blog posts:** the function uses sphinx directives ``blogpost`` and ``blogpostagg`` to create
        a simple blog aggregator. Blog posts will be aggregated by months and categories.
        Link to others parts to the documentation are possible.
        The function also create a file ``rss.xml`` which contains the ten last added blog post.
        This file contains an absolute link to the blog posts. However, because the documentation
        can be published anywhere, the string ``__BLOG_ROOT__`` was inserted
        instead of the absolute url to the website. It must be replaced before uploaded
        or the parameter *blog_root* can be specified in the configuration file ``conf.py``.

    @warning Parameter *add_htmlhelp* calls `Html Help WorkShop
             <https://msdn.microsoft.com/en-us/library/windows/desktop/ms669985%28v=vs.85%29.aspx>`_.
             It also changes the encoding of the HTMLoutput into cp1552 (encoding for Windows)
             instead of utf-8.

    @warning An issue was raised on Linux due to the use of ``.. only:: html``
             (``AttributeError: Can't pickle local object 'setup.<locals>.<lambda>'``).
             It disappeared when using only one thread and not 2 as
             it was previously. Parameter *parallel* was introduced to
             make that change and the default value is not 1.

    .. index:: SVG, Inkscape

    **Others necessary tools:**

    SVG included in a notebook (or any RST file) requires `Inkscape <https://inkscape.org/>`_
    to be converted into Latex.

    .. faqref::
        :title: How to dd an extra layer to the documentation?

        The following `commit <https://github.com/sdpython/python3_module_template/commit/
        75d765a293f65a37b3208601d17d3b0daa891af6>`_
        on project `python3_module_template <https://github.com/sdpython/python3_module_template/>`_
        shows which changes needs to be done to add an extra layer of for the documentation.

    The function assumes :epkg:`IPython` 3 is installed.
    It might no work for earlier versions (notebooks).
    Parameters *from_repo*, *use_run_cmd* were added.
    Notebook conversion to slides is implemented,
    install :epkg:`reveal.js` if not installed.
    Calls the function @see fn _setup_hook to initialize
    the module before generating the documentation.
    Parameter *add_htmlhelp* was added. It runs HtmlHelp on Windows ::

        "C:\\Program Files (x86)\\HTML Help Workshop\\hhc.exe" build\\htmlhelp\\<module>.hhp

    The documentation includes blog (with sphinx command ``.. blogpost::``
    and python scripts ``.. runpython::``. The second command runs a python
    script which outputs RST documntation adds it to the current documentation.
    The function automatically adds custom role and custom directive ``sharenet``.
    The function directly calls
    `sphinx <http://www.sphinx-doc.org/en/stable/>`_,
    `nbconvert <https://nbconvert.readthedocs.io/en/latest/>`_.
    When there are too many notebooks, the notebook index is difficult to read.
    It does not require to get script location.
    Not enough stable from virtual environment.

    Set ``BOKEH_DOCS_MISSING_API_KEY_OK`` to 1.
    bokeh sphinx extension requires that or a key for the google API (???).
    The function was updated to use Sphinx 1.6.2.
    However, you should read blog post
    :ref:`Bug in Sphinx 1.6.2 for custom css <sphinx-162-bug-custom-css>`
    if you have any trouble with custom css.
    Add a report in ``all_notebooks.rst`` about notebook coverage.
    Parameter *parallel* was added.
    The parameter *nblayout* in the configuration file specifies
    the layout for the notebook gallery. ``'classic'`` or ``'table'``.
    The parameter *nbneg_pattern* can be used to remove notebooks from
    the gallery if they match this regular expression.
    It automatically adds video and image directives.
    *remove_unicode* can set to False or True in the documentation
    configuration file to allow or remove unicode characters
    before compiling the latex output.

    .. versionchanged:: 1.7
        Upgrade to Sphinx 1.7. It introduced a breaking
        change with method ``app.status_iterator`` must be
        replaced by ``status_iterator``.
        See issue `bokeh:7520 <https://github.com/bokeh/bokeh/issues/7520>`_.

    .. versionchanged:: 1.8
        Uses own image directive.

    .. versionchanged:: 1.9
        Import ``conf.py`` in a separate process before running
        the generation of the documentation. Do not import it
        directly.
    """
    datetime_rows = [("begin", datetime.now())]

    fLOG("---- JENKINS BEGIN DOCUMENTATION ----")
    if layout is None:
        layout = [("html", "build", {})]
    fLOG("[generate_help_sphinx] ---- layout", layout)
    setup_environment_for_help(fLOG=fLOG)
    # we keep a clean list of modules
    # sphinx configuration is a module and the function loads and unloads it
    list_modules_start = set(sys.modules.keys())

    if add_htmlhelp:  # pragma: no cover
        if not sys.platform.startswith("win"):
            raise ValueError("add_htmlhelp is True and the OS is not Windows")
        fLOG("[generate_help_sphinx] add add_htmlhelp")

    if extra_ext is None:
        extra_ext = []

    def lay_build_override_newconf(t3):
        if isinstance(t3, str):
            lay, build, override, newconf = t3, "build", {}, None
        elif len(t3) == 1:
            lay, build, override, newconf = t3[0], "build", {}, None
        elif len(t3) == 2:
            lay, build, override, newconf = t3[0], t3[1], {}, None
        elif len(t3) == 3:
            lay, build, override, newconf = t3[0], t3[1], t3[2], None
        else:
            lay, build, override, newconf = t3
        return lay, build, override, newconf

    directives.register_directive("blogpost", BlogPostDirective)
    directives.register_directive("blogpostagg", BlogPostDirectiveAgg)
    directives.register_directive("runpython", RunPythonDirective)
    directives.register_directive("sharenet", ShareNetDirective)
    directives.register_directive("video", VideoDirective)
    directives.register_directive("simpleimage", SimpleImageDirective)
    directives.register_directive("image", ImageDirective)
    directives.register_directive("todoext", TodoExt)
    directives.register_directive("mathdef", MathDef)
    directives.register_directive("quote", QuoteNode)
    directives.register_directive("blocref", BlocRef)
    directives.register_directive("exref", ExRef)
    directives.register_directive("faqref", FaqRef)
    directives.register_directive("nbref", NbRef)
    directives.register_directive("cmdref", CmdRef)
    directives.register_directive("postcontents", PostContentsDirective)
    directives.register_directive("tocdelay", TocDelayDirective)
    directives.register_directive("youtube", YoutubeDirective)
    directives.register_directive("thumbnail", ImageDirective)
    directives.register_directive("collapse", CollapseDirective)
    directives.register_directive("gdot", GDotDirective)
    roles.register_canonical_role("sharenet", sharenet_role)
    roles.register_canonical_role("bigger", bigger_role)
    roles.register_canonical_role("githublink", githublink_role)
    roles.register_canonical_role("gitlog", gitlog_role)
    roles.register_canonical_role("tpl", tpl_role)
    roles.register_canonical_role("epkg", epkg_role)
    roles.register_canonical_role("downloadlink", process_downloadlink_role)

    if "conf" in sys.modules:
        raise ImportError(  # pragma: no cover
            "module conf was imported, this function expects not to:\n{0}".format(
                sys.modules["conf"].__file__))

    ############
    # root_source
    ############
    root = os.path.abspath(root)
    froot = root
    root_sphinxdoc = os.path.join(root, "_doc", "sphinxdoc")
    root_source = os.path.join(root_sphinxdoc, "source")
    root_package = os.path.join(root, "src")
    if not os.path.exists(root_package):
        root_package = root
    if not os.path.exists(root_package):
        raise FileNotFoundError(  # pragma: no cover
            "Unable to find source root from '{}'.".format(root))
    fLOG("[generate_help_sphinx] root='{0}'".format(root))
    fLOG("[generate_help_sphinx] root_package='{0}'".format(root_package))
    fLOG("[generate_help_sphinx] root_source='{0}'".format(root_source))
    fLOG("[generate_help_sphinx] root_sphinxdoc='{0}'".format(root_sphinxdoc))
    conf_paths = [root_source, root_package]
    if extra_paths:
        conf_paths.extend(extra_paths)

    ########################################
    # we import conf_base, specific to multi layers
    ########################################
    confb = os.path.join(root_source, "conf_base.py")
    if os.path.exists(confb):  # pragma: no cover
        code = "from conf_base import *"
        with python_path_append(conf_paths):
            try:
                module_conf = execute_script_get_local_variables(
                    code, folder=root_source, check=True)
            except RuntimeError as e:
                raise ImportError("Unable to import conf_base '{}' from '{}'\nsys.path=\n{}".format(
                    confb, root_source, "\n".join(sys.path))) from e

        if module_conf is None:
            raise ImportError(
                "Unable to import '{0}' which defines the help generation".format(confb))
        if 'ERROR' in module_conf:
            msg = "\n".join(["paths:"] + conf_paths + [
                "-----------------------",
                module_conf['ERROR']])
            raise ImportError(msg)
        conf_base = dictionary_as_class(module_conf)
        fLOG("[generate_help_sphinx] conf_base.__file__='{0}'".format(
            os.path.abspath(conf_base.__file__)))  # pylint: disable=E1101

    copypath = list(sys.path)

    # stores static path for every layout, we store them to copy
    html_static_paths = []
    build_paths = []
    all_tocs = []
    parameters = []

    ###################################
    # import others conf, we must do it now
    # it takes too long to do it after if there is an error
    # we assume the configuration are not too different
    # about language for example, latex_path, pandoc_path
    #################################################
    for t3 in layout:
        lay, build, override, newconf = lay_build_override_newconf(t3)
        if newconf is None:
            continue
        fLOG("[generate_help_sphinx] newconf: '{}' - {}".format(newconf, t3))
        # we need to import this file to guess the template directory and
        # add missing templates
        folds = os.path.join(root_sphinxdoc, newconf)
        _import_conf_extract_parameter(root, root_source, folds, build, newconf,
                                       all_tocs, build_paths, parameters,
                                       html_static_paths, fLOG)

    ################################################################
    # we add the source path to the list of path to considered before importing
    # import conf.py
    ################################################################
    with python_path_append(conf_paths):
        try:
            module_conf = execute_script_get_local_variables(
                "from conf import *", folder=root_source, check=True)
        except ImportError as e:  # pragma: no cover
            raise ImportError("Unable to import 'conf.py' from '{0}', sys.path=\n{1}\nBEFORE:\n{2}".format(
                root_source, "\n".join(sys.path), "\n".join(copypath))) from e
        if module_conf is None:
            raise ImportError(  # pragma: no cover
                "unable to import 'conf.py' which defines the help generation")
        if 'ERROR' in module_conf:
            msg = "\n".join(["paths:"] + conf_paths + [
                "----------------------- ERROR:",
                module_conf['ERROR'],
                "------------------------ root_source:",
                root_source])
            raise ImportError(msg)
        if len(module_conf) == 0:
            raise ImportError(
                "No extracted local variable.")  # pragma: no cover
        theconf = dictionary_as_class(module_conf)
    fLOG("[generate_help_sphinx] conf.__file__='{0}'".format(
        os.path.abspath(theconf.__file__)))  # pylint: disable=E1101
    tocs = add_missing_files(root, theconf, "__INSERT__", fLOG)
    all_tocs.extend(tocs)

    ##############################
    # some checkings on the configuration
    ##############################
    _check_sphinx_configuration(theconf, fLOG)

    ##############################################################
    # Extracts variables from the configuration.
    # We store the html_static_path in html_static_paths for the base conf
    # We extract other information from the configuration
    ##############################################################
    html_static_path = theconf.__dict__.get("html_static_path", "phdoc_static")
    if isinstance(html_static_path, list):
        html_static_path = html_static_path[0]
    html_static_path = os.path.join(root_source, html_static_path)
    if not os.path.exists(html_static_path):
        raise FileNotFoundError(  # pragma: no cover
            "no static path:" + html_static_path)
    html_static_paths.append(html_static_path)
    build_paths.append(
        os.path.normpath(os.path.join(html_static_path, "..", "..", "build", "html")))
    custom_latex_processing = theconf.__dict__.get(
        "custom_latex_processing", None)
    if custom_latex_processing is not None:  # pragma: no cover
        # The configuration file is pickled by sphinx
        # and parameter should not be functions.
        if isinstance(custom_latex_processing, str):
            custom_latex_processing = find_custom_latex_processing(  # pylint: disable=E1111
                custom_latex_processing)
        res = custom_latex_processing("dummy phrase")
        if res is None:
            raise ValueError(
                "Result of function custom_latex_processing should not be None.")
    remove_unicode = theconf.__dict__.get("remove_unicode", False)
    snippet_folder = theconf.__dict__.get(
        "notebook_custom_snippet_folder", None)
    if snippet_folder:
        snippet_folder = os.path.join(
            os.path.dirname(theconf.__file__), snippet_folder)  # pylint: disable=E1101

    notebook_replacements = theconf.__dict__.get("notebook_replacements", None)
    if notebook_replacements is not None and not isinstance(notebook_replacements, dict):
        raise TypeError("latex_notebook_replacements should be a dictionary not {0}".format(
            type(notebook_replacements)))

    ####################################
    # modifies the version number in conf.py
    ####################################
    readme = os.path.join(root, "README.rst")
    if not os.path.exists(readme):
        raise FileNotFoundError(readme)  # pragma: no cover
    shutil.copy(readme, root_source)
    license = os.path.join(root, "LICENSE.txt")
    if not os.path.exists(license):
        raise FileNotFoundError(license)  # pragma: no cover
    shutil.copy(license, root_source)
    history = os.path.join(root, "HISTORY.rst")
    if os.path.exists(history):
        dest = os.path.join(root_source, "HISTORY.rst")
        format_history(history, dest)

    ##########
    # language
    ##########
    language = theconf.__dict__.get("language", "en")
    use_sys = theconf.__dict__.get("enable_disabled_parts", None)
    latex_book = theconf.__dict__.get('latex_book', False)
    nbexamples_conf = theconf.__dict__.get('example_gallery_config', None)
    # examples_conf = theconf.__dict__.get('sphinx_gallery_conf', None)

    ##########
    # auto_rst_generation
    ##########
    auto_rst_generation = theconf.__dict__.get("auto_rst_generation", True)

    ospath = os.environ["PATH"]
    latex_path = theconf.__dict__.get("latex_path", find_latex_path())
    # graphviz_dot = theconf.__dict__.get("graphviz_dot", find_graphviz_dot())
    pandoc_path = theconf.__dict__.get("pandoc_path", find_pandoc_path())
    if os.path.isfile(latex_path):
        latex_path = os.path.dirname(latex_path)

    ##########
    # nblinks: references for the notebooks, dictionary {(ref, format): link}
    ##########
    nblayout = theconf.__dict__.get("nblayout", "classic")
    nblinks = theconf.__dict__.get("nblinks", None)
    nbneg_pattern = theconf.__dict__.get("nbneg_pattern", None)
    if nblinks is not None and len(nblinks) > 0:
        fLOG("[generate_help_sphinx] NBLINKS - BEGIN")
        for i, (k, v) in enumerate(sorted(nblinks.items())):
            fLOG("     {0}/{1} - '{2}': '{3}'".format(i + 1, len(nblinks), k, v))
        fLOG("[generate_help_sphinx] NBLINKS - END")
    fLOG("[generate_help_sphinx] nbneg_pattern='{0}'".format(nbneg_pattern))

    # add to PATH
    sep = ";" if sys.platform.startswith("win") else ":"
    if latex_path not in ospath:
        os.environ["PATH"] += sep + latex_path
    if pandoc_path not in ospath:
        os.environ["PATH"] += sep + pandoc_path

    #########
    # changes
    #########
    datetime_rows = [("changes", datetime.now())]
    chan = os.path.join(root, "_doc", "sphinxdoc", "source", "filechanges.rst")
    if "modify_commit" in theconf.__dict__:
        modify_commit = theconf.modify_commit  # pylint: disable=E1101
    else:
        modify_commit = None
    generate_changes_repo(
        chan, root, filter_commit=filter_commit, exception_if_empty=from_repo,
        fLOG=fLOG, modify_commit=modify_commit)

    ######################################
    # we copy javascript dependencies, reveal.js
    ######################################
    datetime_rows = [("javascript", datetime.now())]
    fLOG("[generate_help_sphinx] JAVASCRIPT:", html_static_paths)
    fLOG("[generate_help_sphinx] ROOT:", root_sphinxdoc)
    fLOG("[generate_help_sphinx] BUILD:", build_paths)
    for html_static_path in html_static_paths:
        found = install_javascript_tools(
            root_sphinxdoc, dest=html_static_path, fLOG=fLOG)
        fLOG("[generate_help_sphinx] [javascript]: '{0}'".format(found))

    ############################
    # we copy the extended styles (notebook, snippets)
    ############################
    datetime_rows = [("copy", datetime.now())]
    for html_static_path in html_static_paths:
        dest = os.path.join(html_static_path, style_figure_notebook[0])
        fLOG("    CREATE-CSS", dest)
        with open(dest, "w", encoding="utf-8") as f:
            f.write(style_figure_notebook[1])

    # We should not need that.
    # for build in build_paths:
    #     dest = os.path.join(build, "_downloads")
    #     if not os.path.exists(dest):
    #         os.makedirs(dest)
    #     install_javascript_tools(
    #         root_sphinxdoc, dest=dest, fLOG=fLOG)

    ##############
    # copy the files
    ##############
    fLOG("---- JENKINS BEGIN DOCUMENTATION COPY FILES ----")
    optional_dirs = []
    mapped_function = [(".*[.]%s$" % ext.strip("."), None)
                       for ext in extra_ext]

    ###################################
    # we save the module already imported
    ###################################
    if module_name is None:
        module_name = project_var_name

    sys_modules = set(sys.modules.keys())

    ####################
    # generates extra files
    ####################
    datetime_rows = [("prepare", datetime.now())]
    try:
        dest_doc = os.path.join(root, "_doc", "sphinxdoc", "source")
        fLOG("[generate_help_sphinx] root='{0}'".format(root))
        fLOG("[generate_help_sphinx] dest_doc='{0}'".format(dest_doc))
        subfolders = []
        if root_package.endswith("src"):
            subfolders.append(("src/" + module_name, module_name))
        else:
            subfolders.append((module_name, module_name))
        fLOG("[generate_help_sphinx] subfolders={0}".format(subfolders))
        prepare_file_for_sphinx_help_generation({}, root, dest_doc, subfolders=subfolders, silent=True,
                                                rootrep=("_doc.sphinxdoc.source.%s." % (
                                                    module_name,), ""),
                                                optional_dirs=optional_dirs, mapped_function=mapped_function,
                                                replace_relative_import=False, module_name=module_name,
                                                copy_add_ext=copy_add_ext, use_sys=use_sys, fexclude=fexclude,
                                                auto_rst_generation=auto_rst_generation, fLOG=fLOG)

    except ImportErrorHelpGen as e:  # pragma: no cover
        fLOG(
            "[generate_help_sphinx] major failure, no solution found yet, please run again the script")
        fLOG("[generate_help_sphinx] list of added modules:")
        remove = [k for k in sys.modules if k not in sys_modules]
        for k in sorted(remove):
            fLOG("[generate_help_sphinx]    ", k)

        raise e

    fLOG("[generate_help_sphinx] end of prepare_file_for_sphinx_help_generation")
    fLOG("---- JENKINS END DOCUMENTATION COPY FILES ----")

    ######
    # blog
    ######
    datetime_rows = [("blog", datetime.now())]
    fLOG("---- JENKINS BEGIN DOCUMENTATION BLOGS ----")
    fLOG("[generate_help_sphinx] begin blogs")
    blog_fold = os.path.join(
        os.path.join(root, "_doc/sphinxdoc/source", "blog"))

    if os.path.exists(blog_fold):
        fLOG("[generate_help_sphinx]    BlogPostList")
        plist = BlogPostList(blog_fold, language=language, fLOG=fLOG)
        fLOG("[generate_help_sphinx]    BlogPostList.write_aggregated")
        plist.write_aggregated(blog_fold,
                               blog_title=theconf.__dict__.get(
                                   "blog_title", project_var_name),
                               blog_description=theconf.__dict__.get(
                                   "blog_description", "blog associated to " + project_var_name),
                               blog_root=theconf.__dict__.get("blog_root", "__BLOG_ROOT__"))
    else:
        plist = None

    fLOG("[generate_help_sphinx] end blogs")
    fLOG("---- JENKINS END DOCUMENTATION BLOGS ----")

    ###########
    # notebooks
    ###########
    datetime_rows = [("notebooks", datetime.now())]
    fLOG("---- JENKINS BEGIN DOCUMENTATION NOTEBOOKS ----")
    fLOG("[generate_help_sphinx] begin notebooks")
    indextxtnote = None
    indexlistnote = []
    notebook_dir = os.path.abspath(os.path.join(root, "_doc", "notebooks"))
    notebook_doc = os.path.abspath(
        os.path.join(root, "_doc", "sphinxdoc", "source", "notebooks"))
    if os.path.exists(notebook_dir):
        fLOG("     look into '{0}'".format(notebook_dir))
        fLOG("     -pattern  '{0}'".format(nbneg_pattern))
        notebooks = explore_folder(notebook_dir, pattern=".*[.]ipynb", neg_pattern=nbneg_pattern,
                                   fullname=True, fLOG=fLOG)[1]
        notebooks = [_ for _ in notebooks if (
            "checkpoint" not in _ and "/build/" not in _.replace("\\", "/"))]
        fLOG("     found {0} notebooks".format(len(notebooks)))
        if len(notebooks) > 0:
            fLOG("[generate_help_sphinx] **** notebooks", nbformats)
            build = os.path.join(root, "build", "notebooks")
            if not os.path.exists(build):
                os.makedirs(build)
            indextxtnote = os.path.join(build, "index_notebooks.txt")
            with open(indextxtnote, "w", encoding="utf-8") as f:
                for note in notebooks:
                    no = os.path.relpath(note, notebook_dir)
                    indexlistnote.append((no, note))
                    f.write(no + "\n")
            if not os.path.exists(notebook_doc):
                os.mkdir(notebook_doc)
            nbs_all = process_notebooks(notebooks, build=build, outfold=notebook_doc,
                                        formats=nbformats, latex_path=latex_path,
                                        pandoc_path=pandoc_path, fLOG=fLOG, nblinks=nblinks,
                                        notebook_replacements=notebook_replacements)
            nbs_all = set(_[0]
                          for _ in nbs_all if os.path.splitext(_[0])[-1] == ".rst")
            if len(nbs_all) != len(indexlistnote):  # pragma: no cover
                ext1 = "nbs_all:\n{0}".format("\n".join(nbs_all))
                ext2 = "indexlistnote:\n{0}".format(
                    "\n".join(str(_) for _ in indexlistnote))
                raise ValueError("Different lengths {0} != {1}\n{2}\n{3}".format(
                    len(nbs_all), len(indexlistnote), ext1, ext2))
            nbs = indexlistnote
            fLOG("[generate_help_sphinx] *#* NB, add:", len(nbs))
            nbs.sort()
            build_notebooks_gallery(nbs, os.path.join(
                notebook_doc, "..", "all_notebooks.rst"), layout=nblayout,
                snippet_folder=snippet_folder, fLOG=fLOG)
            build_all_notebooks_coverage(nbs, os.path.join(
                notebook_doc, "..", "all_notebooks_coverage.rst"), module_name, fLOG=fLOG)

        imgs = [os.path.join(notebook_dir, _)
                for _ in os.listdir(notebook_dir) if ".png" in _]
        if len(imgs) > 0:
            gallery_dirs = nbexamples_conf.get(
                'gallery_dirs', None) if nbexamples_conf else None
            for img in imgs:
                shutil.copy(img, notebook_doc)
                if gallery_dirs:
                    for d in gallery_dirs:
                        if not os.path.exists(d):
                            os.makedirs(d)
                        shutil.copy(img, d)
    else:
        fLOG("---- no folder '{0}'".format(notebook_dir))

    fLOG("[generate_help_sphinx] end notebooks")
    fLOG("---- JENKINS END DOCUMENTATION NOTEBOOKS ----")

    #############################################
    # replace placeholder as blog posts list into tocs files
    #############################################
    datetime_rows = [("replace", datetime.now())]
    fLOG("[generate_help_sphinx] blog placeholder")
    if plist is not None:
        replace_placeholder_by_recent_blogpost(
            all_tocs, plist, "__INSERT__", fLOG=fLOG)

    #################################
    #  run the documentation generation
    #################################
    datetime_rows = [("sphinx", datetime.now())]
    fLOG("[generate_help_sphinx] prepare for SPHINX")
    temp = os.environ["PATH"]
    pyts = get_executables_path()
    sepj = ";" if sys.platform.startswith("win") else ":"
    script = sepj.join(pyts)
    fLOG("[generate_help_sphinx] adding " + script)
    temp = script + sepj + temp
    os.environ["PATH"] = temp
    fLOG("[generate_help_sphinx] changing PATH", temp)
    pa = os.getcwd()

    # bokeh trick
    updates_env = dict(BOKEH_DOCS_MISSING_API_KEY_OK=1)
    for k, v in updates_env.items():
        if k not in os.environ:
            os.environ[k] = str(v)

    thispath = os.path.normpath(root)
    docpath = os.path.normpath(os.path.join(thispath, "_doc", "sphinxdoc"))

    ################
    # checks encoding
    ################
    datetime_rows = [("encoding", datetime.now())]
    fLOG("---- JENKINS BEGIN DOCUMENTATION ENCODING ----")
    fLOG("[generate_help_sphinx] checking encoding utf8...")
    for rt, _, files in os.walk(docpath):
        for name in files:
            thn = os.path.join(rt, name)
            if name.endswith(".rst"):
                try:
                    with open(thn, "r", encoding="utf8") as f:
                        f.read()
                except UnicodeDecodeError as e:  # pragma: no cover
                    raise HelpGenException(
                        "issue with encoding in a file", thn) from e
                except Exception as e:  # pragma: no cover
                    raise HelpGenException("issue with file ", thn) from e

    fLOG("[generate_help_sphinx] running sphinx... from", docpath)
    if not os.path.exists(docpath):
        raise FileNotFoundError(docpath)
    fLOG("---- JENKINS END DOCUMENTATION ENCODING ----")

    os.chdir(docpath)

    #####################
    # builds command lines
    #####################
    datetime_rows = [("build", datetime.now())]
    fLOG("[generate_help_sphinx] sphinx command lines")
    cmds = []
    lays = []
    cmds_post = []
    for t3 in layout:
        lay, build, override, newconf = lay_build_override_newconf(t3)

        if lay == "pdf":
            lay = "elatex"

        if clean and sys.platform.startswith("win"):
            if os.path.exists(build):
                for fold in os.listdir(build):
                    remove_folder(os.path.join(build, fold))
                remove_folder(build)

        over_ = ["{0}={1}".format(k, v) for k, v in override.items()]
        over = []
        for o in over_:
            over.append("-D")
            over.append(o)

        sconf = [] if newconf is None else ["-c", newconf]

        cmd = ["sphinx-build", "-j%d" % parallel, "-v", "-T", "-b", "{0}".format(lay),
               "-d", "{0}/doctrees".format(build)] + over + sconf + ["source", "{0}/{1}".format(build, lay)]
        if lay in ('latex', 'pdf', 'elatex'):
            cmd.extend(["-D", "imgmath_image_format=png"])
        cmds.append((cmd, build, lay))
        fLOG("[generate_help_sphinx] run:", cmd)
        lays.append(lay)

        if add_htmlhelp and lay == "html":  # pragma: no cover
            # we cannot execute htmlhelp in the same folder
            # as it changes the encoding
            cmd = ["sphinx-build", "-j%d" % parallel, "-v", "-T", "-b", "{0}help".format(lay),
                   "-d", "{0}/doctrees".format(build)] + over + sconf + ["source", "{0}/{1}html".format(build, lay)]
            cmd.extend(["-D", "imgmath_image_format=png"])
            cmds.append((cmd, build, "add_htmlhelp"))
            fLOG("[generate_help_sphinx] run:", cmd)
            lays.append(lay)
            hhp = os.path.join(build, lay + "help", module_name + "_doc.hhp")
            cmdp = '"C:\\Program Files (x86)\\HTML Help Workshop\\hhc.exe" ' + \
                '"%s"' % hhp
            cmds_post.append(cmdp)

    # cmd = "make {0}".format(lay)

    ###############################################################
    # run cmds (prefer to use os.system instead of run_cmd if it gets stuck)
    ###############################################################
    datetime_rows = [("cmd", datetime.now())]
    fLOG("[generate_help_sphinx] RUN SPHINX")
    for cmd, build, kind in cmds:
        fLOG("---- JENKINS BEGIN DOCUMENTATION SPHINX ----")
        fLOG(
            "##################################################################################################")
        fLOG(
            "##################### run sphinx #################################################################")
        fLOG(
            "##################################################################################################")
        fLOG("[generate_help_sphinx]", cmd)
        fLOG("[generate_help_sphinx] from ", os.getcwd())
        fLOG("[generate_help_sphinx] PATH ", os.environ["PATH"])

        existing = list(sorted(sys.modules.keys()))
        for ex in existing:
            if ex[0] == '_':
                doesrem = False
            elif ex not in list_modules_start:
                doesrem = True
                for pr in ('pywintypes', 'pandas', 'IPython', 'jupyter', 'numpy', 'scipy', 'matplotlib',
                           'pyquickhelper', 'yaml', 'xlsxwriter', '_csv',
                           '_lsprof', '_multiprocessing', '_overlapped', '_sqlite3',
                           'alabaster', 'asyncio', 'babel', 'bokeh', 'cProfile',
                           'certifi', 'colorsys', 'concurrent', 'csv', 'cycler',
                           'dateutil', 'decorator', 'docutils', 'fractions', 'gc',
                           'getopt', 'getpass', 'hmac', 'http', 'imp', 'ipython_genutils',
                           'jinja2', 'mimetypes', 'multiprocessing', 'pathlib',
                           'pickleshare', 'profile', 'prompt_toolkit', 'pstats',
                           'pydoc', 'py', 'pygments', 'requests', 'runpy', 'simplegeneric',
                           'sphinx', 'sqlite3', 'tornado', 'traitlets', 'typing', 'wcwidth',
                           'pythoncom', 'distutils', 'six', 'webbrowser', 'win32api', 'win32com',
                           'sphinxcontrib', 'zmq', 'nbformat', 'nbconvert',
                           'encodings', 'entrypoints', 'html', 'ipykernel', 'isodate',
                           'jsonschema', 'jupyter_client', 'mistune', 'nbbrowserpdf',
                           'notebook', 'pyparsing', 'zmq', 'jupyter_core',
                           'timeit', 'sphinxcontrib_images_lightbox2', 'win32con'):
                    if ex == pr or ex.startswith(pr + "."):
                        doesrem = False
            else:
                doesrem = False
            if doesrem:
                fLOG(
                    "[generate_help_sphinx] remove '{0}' from sys.modules".format(ex))
                del sys.modules[ex]

        fLOG(
            "##################################################################################################")
        fLOG("[generate_help_sphinx] direct_call={0}".format(direct_call))
        fLOG("[generate_help_sphinx] cmd='''{0}'''".format(cmd))
        if isinstance(cmd, list):
            fLOG("[generate_help_sphinx] cmd='''{0}'''".format(" ".join(cmd)))
        fLOG("[generate_help_sphinx] kind='{0}'".format(kind))
        fLOG("[generate_help_sphinx] build='{0}'".format(build))
        fLOG("[generate_help_sphinx] direct_call={0}".format(direct_call))

        # direct call
        with python_path_append(root_source):
            if direct_call:
                # mostly to debug
                out = StringIO()
                err = StringIO()
                memo_out = sys.stdout
                memo_err = sys.stderr
                sys.stdout = out
                sys.stderr = out
                try:
                    build_main(cmd[1:])
                except SystemExit as e:  # pragma: no cover
                    raise SystemExit("Unable to run Sphinx\n--CMD\n{0}\n--ERR--\n{1}\n--CWD--\n{2}\n--OUT--\n{3}\n--".format(
                        cmd, err.getvalue(), os.getcwd(), out.getvalue())) from e
                sys.stdout = memo_out
                sys.stderr = memo_err
                out = out.getvalue()
                err = err.getvalue()
                lines = ['***OUT/***'] + out.split('\n') + ['***OUT\\***']
                lines = [
                    _ for _ in lines if "toctree contains reference to document 'blog/" not in _]
                out = "\n".join(lines)
            else:
                def customfLOG(*args, **kwargs):
                    "filter out some lines"
                    args = [
                        _ for _ in args if "toctree contains reference to document 'blog/" not in _]
                    if args:
                        fLOG(*args, **kwargs)

                out, err = _process_sphinx_in_private_cmd(cmd, fLOG=customfLOG)
                lines = ['***OUT//***'] + out.split('\n') + ['***OUT\\\\***']
                lines = [
                    _ for _ in lines if "toctree contains reference to document 'blog/" not in _]
                out = "\n".join(lines)

        fLOG("[generate_help_sphinx] end cmd len(out)={0} len(err)={1}".format(
            len(out), len(err)))

        if len(err) > 0 or len(out) > 0:
            if (len(err) > 0 and "Exception occurred:" in err) or \
               (len(out) > 0 and "Exception occurred:" in out):
                def keep_line(_):  # pragma: no cover
                    if "RemovedInSphinx" in _:
                        return False
                    if "while setting up extension" in _:
                        return False
                    if "toctree contains reference to document 'blog/" in _:
                        return False
                    return True
                out = "\n".join(
                    filter(lambda _: keep_line(_), out.split("\n")))
                raise HelpGenException(
                    "Sphinx raised an exception (direct_call={3})\n--CMD--\n{0}\n--OUT--\n{1}\n[sphinxerror]-3\n{2}".format(
                        cmd, out, err, direct_call))

            fLOG("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            fLOG("[generate_help_sphinx]", kind, "~~~~", cmd)
            fLOG("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            warnings.warn(
                "Sphinx went through errors. Check if any of them is important.\n---OUT---\n{0}\n[sphinxerror]-2\n{1}\n----".format(
                    out, err), UserWarning)
            fLOG("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

        if kind == "html":
            fLOG(
                "##############################################################")
            fLOG("[generate_help_sphinx] check that index.html exists")
            findex = os.path.join(build, kind, "index.html")
            if not os.path.exists(findex):
                raise FileNotFoundError("something went wrong, unable to find {0}\nCMD\n{1}\nOUT\n{2}\nERR\n{3}\nLAY\n{4}\nINDEX\n{5}"
                                        .format(findex, cmd, out, err, kind, os.path.abspath(findex)))

            fLOG(
                "##############################################################")
            verification_html_format(os.path.join(build, kind), fLOG=fLOG)

        fLOG(
            "##################################################################################################")
        fLOG(
            "##################### end run sphinx #############################################################")
        fLOG(
            "##################################################################################################")
        fLOG("---- JENKINS END DOCUMENTATION SPHINX ----")

    # we copy the extended styles (notebook, snippets) (again in build folders)
    # we should not need that
    for build_path in build_paths:
        if not os.path.exists(build_path):
            fLOG("[generate_help_sphinx]    build_path not found '{0}'".format(
                build_path))
            continue
        dest = os.path.join(build_path, "_static", style_figure_notebook[0])
        if not os.path.exists(dest):  # pragma: no cover
            fLOG("[generate_help_sphinx]    CREATE-CSS2", dest)
            with open(dest, "w", encoding="utf-8") as f:
                f.write(style_figure_notebook[1])

    if add_htmlhelp:  # pragma: no cover
        # we call HtmlHelp
        fLOG("[generate_help_sphinx] run HTMLHELP")
        for cmd in cmds_post:
            fLOG("running", cmd)
            out, err = run_cmd(cmd, wait=True, fLOG=fLOG,
                               communicate=True, timeout=600)
            fLOG(out)
            if len(err) > 0:
                mes = "Sphinx went through errors. Check if any of them is important.\nOUT:\n{0}\n[sphinxerror]-1\n{1}"
                warnings.warn(mes.format(out, err), UserWarning)
        fLOG("[generate_help_sphinx] end run HTMLHELP")

    #####################################
    # we copy some file such as rss.xml
    #####################################
    fLOG("---- JENKINS BEGIN COPY RSS.XML ----")
    tocopy = [os.path.join(docpath, "source", "blog", "rss.xml")]
    for toco in tocopy:
        if os.path.exists(toco):
            fLOG("[generate_help_sphinx] copy '{}'".format(
                os.path.split(toco)[-1]))
            for build_path in build_paths:
                dest = os.path.join(build_path, "_downloads")
                if os.path.exists(dest):
                    shutil.copy(toco, dest)
        else:
            fLOG("[generate_help_sphinx] not found '{}'".format(
                os.path.split(toco)[-1]))

    fLOG("---- JENKINS END COPY RSS.XML ----")

    #####################################
    # we copy the coverage files if it is missing
    #####################################
    datetime_rows = [("converage", datetime.now())]
    fLOG("---- JENKINS BEGIN DOCUMENTATION COVERAGE ----")
    fLOG("[generate_help_sphinx] copy coverage")
    covfold = os.path.join(docpath, "source", "coverage")
    if os.path.exists(covfold):  # pragma: no cover
        fLOG("[generate_help_sphinx] coverage folder:", covfold)
        allfiles = os.listdir(covfold)
        allf = [_ for _ in allfiles if _.endswith(".rst")]
        if len(allf) == 0:
            # no rst file --> we copy
            allfiles = [os.path.join(covfold, _) for _ in allfiles]
            allfiles = [_ for _ in allfiles if os.path.isfile(_)]
            for lay in lays:
                layfolder = os.path.join(docpath, build, lay)
                fLOG("[generate_help_sphinx] coverage docpath:", docpath, " -- ",
                     build, " -- ", lay, " ---- ", layfolder)
                if os.path.exists(layfolder):
                    covbuild = os.path.join(layfolder, "coverage")
                    fLOG("[coverage] covbuild", covbuild)
                    if not os.path.exists(covbuild):
                        os.mkdir(covbuild)
                    for f in allfiles:
                        fLOG("[generate_help_sphinx] coverage copy ",
                             f, " to ", covbuild)
                        shutil.copy(f, covbuild)
        else:
            fLOG("[sphinxerror]-B coverage files with rst in", covfold)
    else:
        fLOG("[generate_help_sphinx] no coverage files", covfold)
    fLOG("---- JENKINS END DOCUMENTATION COVERAGE ----")

    #########################################################
    # we copy javascript dependencies to build _download/javascript
    #########################################################
    datetime_rows = [("javascript", datetime.now())]
    # for every layout
    fLOG("[generate_help_sphinx] [reveal.js] JAVASCRIPT: COPY", html_static_paths)
    fLOG("[generate_help_sphinx] [reveal.js] BUILD:", build_paths)
    for subf in ["html"]:
        for html_static_path, build_path in zip(html_static_paths, build_paths):
            for sname in ["_downloads", "notebooks"]:
                builddoc = os.path.join(build_path, subf, sname)
                if not os.path.exists(builddoc):
                    builddoc = os.path.join(build_path, "..", subf, sname)
                if not os.path.exists(builddoc):
                    builddoc = os.path.join(build_path, sname)
                if os.path.exists(builddoc):
                    # no download, there is probably no notebooks
                    # so it is not needed
                    fLOG("[generate_help_sphinx] copy javascript static files from",
                         html_static_path, "to", builddoc)
                    copy = synchronize_folder(
                        html_static_path, builddoc, copy_1to2=True, fLOG=fLOG)
                    fLOG("[generate_help_sphinx] javascript",
                         len(copy), "files copied")
                else:
                    fLOG(
                        "[generate_help_sphinx] [reveal.js] no need, no folder", builddoc)

    ######
    # next
    ######
    datetime_rows = [("latex", datetime.now())]
    fLOG("[generate_help_sphinx] LATEX")
    if "latex" in layout or "elatex" in layout:
        fLOG("[generate_help_sphinx] post_process_latex_output", froot)
        post_process_latex_output(
            froot, False, custom_latex_processing=custom_latex_processing)

    if "pdf" in layout:
        fLOG("[generate_help_sphinx] compile_latex_output_final",
             froot, "**", latex_path)
        compile_latex_output_final(
            froot, latex_path, False, latex_book=latex_book, fLOG=fLOG,
            custom_latex_processing=custom_latex_processing,
            remove_unicode=remove_unicode)

    if "html" in layout:
        nbf = os.path.join(build, "html", "notebooks")
        if os.path.exists(nbf):
            post_process_html_nb_output_static_file(nbf, fLOG=fLOG)
            post_process_html_nb_output_static_file(
                os.path.join(build, "html", "_downloads"), fLOG=fLOG)

    for build_path in build_paths:
        src = os.path.join(build_path, "_images")
        dest = os.path.join(build_path, "notebooks")
        if os.path.exists(src) and os.path.exists(dest):
            fLOG("[generate_help_sphinx] [imgs] look for images in ", src)
            for img in enumerate_copy_images_for_slides(src, dest):
                fLOG("[generate_help_sphinx] [imgs]    copy image for slides:", img)

    ######
    # copy pdf to html
    ######
    latex = os.path.join(build_path, "latex")
    html = os.path.join(build_path, "latex")
    if os.path.exists(html) and os.path.exists(latex):  # pragma: no cover
        pdfs = os.listdir(latex)
        for pdf in pdfs:
            ext = os.path.splitext(pdf)[-1]
            if ext != '.pdf':
                continue
            full = os.path.join(latex, pdf)
            fLOG("[generate_help_sphinx] [pdf] copy:", pdf)
            shutil.copy(full, html)

    #####
    # end
    #####
    os.chdir(pa)
    fLOG("################################")
    fLOG("#### END - check log for success")
    fLOG("################################")
    for i, row in enumerate(datetime_rows):
        if i == 0:
            a = row[1]
        else:
            a = datetime_rows[i - 1][1]
        b = row[1]
        d = b - a
        mes = "[generate_help_sphinx] {0}{1}: {2} [{3} --> {4}]".format(
            row[0], " " * (15 - len(row[0])), d, a, b)
        fLOG(mes)
    fLOG("---- JENKINS END DOCUMENTATION ----")


def _process_sphinx_in_private_cmd(list_args, fLOG):
    this = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), "process_sphinx_cmd.py")
    res = []
    for i, c in enumerate(list_args):
        if i == 0 and c in ("sphinx-main", "sphinx-build"):
            continue
        if c[0] == '"' or c[-1] == '"' or ' ' not in c:
            res.append(c)
        else:
            res.append('"{0}"'.format(c))
    sargs = " ".join(res)
    cmd = '"{0}" "{1}" {2}'.format(
        sys.executable.replace("w.exe", ".exe"), this, sargs)
    fLOG("    ", cmd)
    fLOG("[generate_help_sphinx] _process_sphinx_in_private_cmd BEGIN")
    out, err = run_cmd(cmd, wait=True, fLOG=fLOG,
                       communicate=False, tell_if_no_output=120)
    fLOG("[generate_help_sphinx] _process_sphinx_in_private_cmd END")
    lines = out.split('\n')
    lines = [
        _ for _ in lines if "toctree contains reference to document 'blog/" not in _]
    out = "\n".join(lines)
    return out, err


def _check_sphinx_configuration(conf, fLOG):
    """
    Operates some verification on the configuration.

    @param  conf        :epkg:`sphinx` configuration
    @param  fLOG        logging function
    """
    clean_folders = []
    if hasattr(conf, "sphinx_gallery_conf"):
        sphinx_gallery_conf = conf.sphinx_gallery_conf
        if len(sphinx_gallery_conf["examples_dirs"]) != len(sphinx_gallery_conf["gallery_dirs"]):
            add = "\nexamples_dirs={0}\ngallery_dirs={1}".format(
                sphinx_gallery_conf["examples_dirs"], sphinx_gallery_conf["gallery_dirs"])
            raise ValueError(
                'sphinx_gallery_conf["examples_dirs"] and sphinx_gallery_conf["gallery_dirs"] do not have the same size.' + add)
        if len(sphinx_gallery_conf["examples_dirs"]) > 0:
            fLOG(
                "[sphinx-gallery] {0} discovered".format(len(sphinx_gallery_conf["examples_dirs"])))
            for a, b in zip(sphinx_gallery_conf["examples_dirs"],
                            sphinx_gallery_conf["gallery_dirs"]):
                fLOG("[sphinx-gallery]    src  '{0}'".format(a))
                fLOG("[sphinx-gallery]    dest '{0}'".format(b))
                clean_folders.append(a)
    for cl in clean_folders:
        fLOG("[sphinx-gallery] clean '{0}'".format(cl))
        for temp in os.listdir(cl):  # pragma: no cover
            if temp.startswith("temp_"):
                aaa = os.path.join(cl, temp)
                fLOG("[sphinx-gallery] remove '{0}'".format(cl))
                remove_folder(aaa)


def _import_conf_extract_parameter(root, root_source, folds, build, newconf,
                                   all_tocs, build_paths, parameters,
                                   html_static_paths, fLOG):
    """
    Imports the configuration file and extracts some
    of the parameters it defines.
    Fills the following lists.

    @param      root                folder of the package
    @param      root_source         folder of the sources
    @param      folds               folder of the documentation
    @param      build               build path
    @param      newconf             unused except in an error message
    @param      all_tocs            list to fill
    @param      build_paths         list to fill
    @param      parameters          list to fill
    @param      html_static_paths   list to fill
    @param      fLOG                logging function

    * all_tocs
    * build_paths
    * parameters
    * html_static_paths
    """
    # trick, we place the good folder in the first position
    with python_path_append(folds):
        if fLOG:
            fLOG(
                "[_import_conf_extract_parameter] import from '{0}'".format(folds))
        try:
            module_conf = execute_script_get_local_variables(
                "from conf import *", folder=folds)
        except Exception as ee:  # pragma: no cover
            raise HelpGenException(
                "Unable to import a config file (root_source='{0}').".format(
                    folds), os.path.join(folds, "conf.py")) from ee
        if 'ERROR' in module_conf:
            raise ImportError("\n" + module_conf['ERROR'] + "\n")
        if len(module_conf) == 0:
            raise ImportError("Unable to extract local variable from conf.py.")

    if module_conf is None:
        raise ImportError(  # pragma: no cover
            "Unable to import '{0}' which defines the help generation".format(newconf))
    thenewconf = dictionary_as_class(module_conf)
    if fLOG:
        fLOG("[_import_conf_extract_parameter] import:", thenewconf.drop(
            "epkg_dictionary", "latex_elements", "imgmath_latex_preamble", "preamble"))

    tocs = add_missing_files(root, thenewconf, "__INSERT__", fLOG)
    all_tocs.extend(tocs)

    # we store the html_static_path in html_static_paths
    html_static_path = thenewconf.__dict__.get(
        "html_static_path", "phdoc_static")
    if isinstance(html_static_path, list):
        html_static_path = html_static_path[0]
    html_static_path = os.path.normpath(
        os.path.join(root_source, html_static_path))
    if not os.path.exists(html_static_path):
        raise FileNotFoundError(  # pragma: no cover
            "no static path:" + html_static_path)
    html_static_paths.append(html_static_path)
    build_paths.append(
        os.path.normpath(os.path.join(html_static_path, "..", "..", build, "html")))
    pp = dict(latex_book=thenewconf.latex_book)  # pylint: disable=E1101
    parameters.append(pp)
