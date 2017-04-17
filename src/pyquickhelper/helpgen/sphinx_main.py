# -*- coding: utf-8 -*-
"""
@file
@brief Contains the main function to generate the documentation
for a module designed the same way as this one, @see fn generate_help_sphinx.

.. todoext::
    :title: Add support for sphinx-gallery
    :tag: done
    :date: 2016-12-18
    :cost: 1
    :release: 1
    :issue: 36

    The default configuration pyquickhelper is setting up
    automatically considers folder ``_doc\\examples``
    and add it to the documentation. To add a link to the gallery:
    ``examples/index``.
"""
import os
import sys
import shutil
import importlib
import warnings
from docutils.parsers.rst import directives, roles
from sphinx import build_main
from ..filehelper import remove_folder
from ..loghelper.flog import run_cmd, fLOG
from .utils_sphinx_doc import prepare_file_for_sphinx_help_generation
from .utils_sphinx_doc_helpers import HelpGenException, ImportErrorHelpGen
from .conf_path_tools import find_latex_path, find_pandoc_path
from ..filehelper.synchelper import explore_folder
from .utils_sphinx_config import ie_layout_html
from ..sphinxext.blog_post_list import BlogPostList
from ..sphinxext.sphinx_blog_extension import BlogPostDirective, BlogPostDirectiveAgg
from ..sphinxext.sphinx_runpython_extension import RunPythonDirective
from ..sphinxext.sphinx_sharenet_extension import ShareNetDirective, sharenet_role
from ..sphinxext.sphinx_bigger_extension import bigger_role
from ..sphinxext.sphinx_githublink_extension import githublink_role
from ..sphinxext.sphinx_mathdef_extension import MathDef
from ..sphinxext.sphinx_blocref_extension import BlocRef
from ..sphinxext.sphinx_exref_extension import ExRef
from ..sphinxext.sphinx_faqref_extension import FaqRef
from ..sphinxext.sphinx_nbref_extension import NbRef
from ..sphinxext.sphinx_todoext_extension import TodoExt
from .post_process import post_process_latex_output
from .process_notebooks import process_notebooks, build_notebooks_gallery
from .sphinx_helper import post_process_html_nb_output_static_file
from .install_js_dep import install_javascript_tools
from ..filehelper import synchronize_folder
from .sphinx_main_helper import setup_environment_for_help, get_executables_path, generate_changes_repo
from .sphinx_main_helper import compile_latex_output_final, replace_placeholder_by_recent_blogpost, enumerate_copy_images_for_slides
from .sphinx_main_verification import verification_html_format
from .sphinx_main_missing_html_files import add_missing_files
from .style_css_template import style_figure_notebook


if sys.version_info[0] == 2:
    from codecs import open
    from StringIO import StringIO
else:
    from io import StringIO

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
                                    "rst", "pdf", "present", "github"),
                         # ("epub", "build", {})],
                         layout=None,
                         module_name=None, from_repo=True, add_htmlhelp=False,
                         copy_add_ext=None, direct_call=False, fLOG=fLOG):
    """
    runs the help generation
        - copies every file in another folder
        - replaces comments in doxygen format into rst format
        - replaces local import by global import (tweaking sys.path too)
        - calls sphinx to generate the documentation.

    @param      project_var_name    project name
    @param      clean               if True, cleans the previous documentation first (html files)
    @param      root                see below
    @param      filter_commit       function which accepts a commit to show on the documentation (based on the comment)
    @param      extra_ext           list of file extensions to document (not .py)
    @param      nbformats           requested formats for the notebooks conversion
    @param      layout              list of formats sphinx should generate such as html, latex, pdf, docx,
                                    it is a list of tuple (layout, build directory, parameters to override),
                                    if None --> ``[("html", "build", {})]``
    @param      module_name         name of the module (must be the folder name src/*name*, if None, *module_name*
                                    will be replaced by *project_var_name*
    @param      from_repo           if True, assumes the sources come from a source repository,
                                    False otherwise
    @param      add_htmlhelp        run HTML Help too (only on Windows)
    @param      copy_add_ext        additional file extension to copy
    @param      direct_call         direct call to sphinx with *sphinx_build* if *True*
                                    or run a command line in an another process to get
                                    a clear environment
    @param      fLOG                logging function

    The result is stored in path: ``root/_doc/sphinxdoc/source``.
    We assume the file ``root/_doc/sphinxdoc/source/conf.py`` exists
    as well as ``root/_doc/sphinxdoc/source/index.rst``.

    If you generate latex/pdf files, you should add variables ``latex_path`` and ``pandoc_path``
    in your file ``conf.py`` which defines the help.

    You can exclud some part while generating the documentation by adding:

    * ``# -- HELP BEGIN EXCLUDE --``
    * ``# -- HELP END EXCLUDE --``

    @code
    latex_path  = r"C:/Program Files/MiKTeX 2.9/miktex/bin/x64"
    pandoc_path = r"%USERPROFILE%/AppData/Local/Pandoc"
    @endcode

    .. exref::
        :title: Run help generation
        :index: extension, extra extension, ext

        @code
        # from the main folder which contains folder src
        generate_help_sphinx("pyquickhelper")
        @endcode

    By default, the function only consider files end by ``.py`` and ``.rst`` but you could
    add other files sharing the same extensions by adding this one
    in the ``extra_ext`` list.

    .. exref::
        :title: Other page of examples___run help generation

        This example is exactly the same as the previous one but will be generated on another page of examples.
        @code
        # from the main folder which contains folder src
        generate_help_sphinx("pyquickhelper")
        @endcode

    .. exref::
        :title: Page with an accent -é- in the title___run help generation

        Same page with an accent.
        @code
        # from the main folder which contains folder src
        generate_help_sphinx("pyquickhelper")
        @endcode

    The function requires:

    - pandoc
    - latex

    @warning Some themes such as `Bootstrap Sphinx Theme <http://ryan-roemer.github.io/sphinx-bootstrap-theme/>`_
             do not work on Internet Explorer. In that case, the
             file ``<python_path>/Lib/site-packages/sphinx/themes/basic/layout.html``
             must be modified to add the following line (just below ``Content-Type``).

             @code
             <meta http-equiv="X-UA-Compatible" content="IE=edge" />
             @endcode

    .. index:: PEP8, autopep8

    The code should follow as much as possible the sytle convention
    `PEP8 <https://www.python.org/dev/peps/pep-0008/>`_.
    The module `autopep8 <https://pypi.python.org/pypi/autopep8>`_ can modify a file or all files contained in one folder
    by running the following command line::

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

    @warning Parameter *add_htmlhelp* calls `Html Help WorkShop <https://msdn.microsoft.com/en-us/library/windows/desktop/ms669985%28v=vs.85%29.aspx>`_.
             It also changes the encoding of the HTMLoutput into cp1552 (encoding for Windows)
             instead of utf-8.

    .. index:: SVG, Inkscape

    **Others necessary tools:**

    SVG included in a notebook (or any RST file) requires `Inkscape <https://inkscape.org/>`_
    to be converted into Latex.

    .. faqref::
        :title: How to dd an extra layer to the documentation?

        The following `commit <https://github.com/sdpython/python3_module_template/commit/75d765a293f65a37b3208601d17d3b0daa891af6>`_
        on project `python3_module_template <https://github.com/sdpython/python3_module_template/>`_
        shows which changes needs to be done to add an extra layer of for the documentation.

    .. versionchanged:: 1.0
        Assumes IPython 3 is installed. It might no work for earlier versions (notebooks).
        Parameters *from_repo*, *use_run_cmd* were added.

    .. versionchanged:: 1.1
        Add notebook conversion to slides, install reveal.js if not installed.
        Calls the function @see fn _setup_hook to initialize the module before
        generating the documentation.
        Parameter *add_htmlhelp* was added. It runs HtmlHelp on Windows ::

            "C:\\Program Files (x86)\\HTML Help Workshop\\hhc.exe" build\\htmlhelp\\<module>.hhp

    .. versionadded:: 1.2
        The documentation includes blog (with sphinx command ``.. blogpost::``
        and python scripts ``.. runpython::``. The second command runs a python
        script which outputs RST documntation adds it to the current documentation.

    .. versionadded:: 1.3
        Parameters *copy_add_ext*, *fLOG* were added.
        Automatically add custom role and custom directive ``sharenet``.

    .. versionchanged:: 1.4
        Replace command line by direct call to
        `sphinx <http://www.sphinx-doc.org/en/stable/>`_,
        `nbconvert <https://nbconvert.readthedocs.io/en/latest/>`_,
        `nbpresent <https://github.com/Anaconda-Platform/nbpresent>`_.
        Remove parameter *use_run_cmd*.

    .. versionchanged:: 1.5
        Set ``BOKEH_DOCS_MISSING_API_KEY_OK`` to 1.
        bokeh sphinx extension requires that or a key for the google API (???).

    .. todoext::
        :title: add subfolder when building indexes of notebooks
        :tag: enhancement
        :issue: 9
        :cost: 1
        :release: 1.4
        :date: 2016-08-23
        :hidden:

        When there are too many notebooks, the notebook index is difficult to read.

    .. todoext::
        :title: replace command line by direct call to sphinx, nbconvert, nbpresent
        :tag: enhancement
        :issue: 30
        :cost: 3
        :release: 1.4
        :date: 2016-08-25
        :hidden:

        It does not require to get script location.
        Not enough stable from virtual environment.
    """
    if layout is None:
        layout = [("html", "build", {})]
    setup_environment_for_help(fLOG=fLOG)
    # we keep a clean list of modules
    # sphinx configuration is a module and the function loads and unloads it
    list_modules_start = set(sys.modules.keys())

    if add_htmlhelp:
        if not sys.platform.startswith("win"):
            raise ValueError("add_htmlhelp is True and the OS is not Windows")
        else:
            fLOG("~~~~~~~~~~~~~~~~~~~~~~ add add_htmlhelp")

    if extra_ext is None:
        extra_ext = []

    def lay_build_override_newconf(t3):
        if isinstance(t3, str  # unicode#
                      ):
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
    directives.register_directive("todoext", TodoExt)
    directives.register_directive("mathdef", MathDef)
    directives.register_directive("blocref", BlocRef)
    directives.register_directive("exref", ExRef)
    directives.register_directive("faqref", FaqRef)
    directives.register_directive("nbref", NbRef)
    roles.register_canonical_role("sharenet", sharenet_role)
    roles.register_canonical_role("bigger", bigger_role)
    roles.register_canonical_role("githublink", githublink_role)

    if "conf" in sys.modules:
        raise ImportError("module conf was imported, this function expects not to:\n{0}".format(
            sys.modules["conf"].__file__))

    ############
    # root_source
    ############
    root = os.path.abspath(root)
    froot = root
    root_sphinxdoc = os.path.join(root, "_doc", "sphinxdoc")
    root_source = os.path.join(root_sphinxdoc, "source")

    ########################################
    # we import conf_base, specific to multi layers
    ########################################
    confb = os.path.join(root_source, "conf_base.py")
    if os.path.exists(confb):
        try:
            import conf_base
        except ImportError as e:
            sys.path.append(root_source)
            import conf_base
            del sys.path[-1]

        fLOG("~~~~ conf_base", conf_base.__file__)

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
        fLOG("~~~~ newconf:", newconf, t3)
        if newconf is None:
            continue
        # we need to import this file to guess the template directory and
        # add missing templates
        folds = os.path.join(root_sphinxdoc, newconf)
        # trick, we place the good folder in the first position
        sys.path.insert(0, folds)
        fLOG("~~~~ import from", folds)
        try:
            thenewconf = importlib.import_module("conf")
            fLOG("~~~~ import:", thenewconf)
        except Exception as ee:
            raise HelpGenException(
                "unable to import a config file (t3={0}, root_source={1})".format(
                    t3, root_source),
                os.path.join(folds, "conf.py")) from ee

        # we remove the insert path
        del sys.path[0]
        if thenewconf is None:
            raise ImportError(
                "unable to import {0} which defines the help generation".format(newconf))
        tocs = add_missing_files(root, thenewconf, "__INSERT__")
        all_tocs.extend(tocs)
        del sys.modules["conf"]

        # check if we need to run ie_layout_html
        check_ie_layout_html = thenewconf.__dict__.get(
            "check_ie_layout_html", True)
        if check_ie_layout_html:
            ie_layout_html()

        # we store the html_static_path in html_static_paths
        html_static_path = thenewconf.__dict__.get(
            "html_static_path", "phdoc_static")
        if isinstance(html_static_path, list):
            html_static_path = html_static_path[0]
        html_static_path = os.path.join(root_source, html_static_path)
        if not os.path.exists(html_static_path):
            raise FileNotFoundError("no static path:" + html_static_path)
        html_static_paths.append(html_static_path)
        build_paths.append(
            os.path.normpath(os.path.join(html_static_path, "..", "..", build, "html")))
        parameters.append(dict(latex_book=thenewconf.latex_book))

    ################################################################
    # we add the source path to the list of path to considered before importing
    ################################################################
    sys.path.append(root_source)

    ###############
    # import conf.py
    ###############
    try:
        theconf = importlib.import_module('conf')
    except ImportError as e:
        if sys.version_info[0] == 2:
            # we start again because we lose track of the exception
            theconf = importlib.import_module('conf')
        raise ImportError("unable to import conf.py from {0}, sys.path=\n{1}\nBEFORE:\n{2}".format(
            root_source, "\n".join(sys.path), "\n".join(copypath))) from e
    if theconf is None:
        raise ImportError(
            "unable to import conf.py which defines the help generation")
    tocs = add_missing_files(root, theconf, "__INSERT__")
    all_tocs.extend(tocs)

    ##############################################################
    # we store the html_static_path in html_static_paths for the base conf
    # we extract other information from the configuration
    ##############################################################
    html_static_path = theconf.__dict__.get("html_static_path", "phdoc_static")
    if isinstance(html_static_path, list):
        html_static_path = html_static_path[0]
    html_static_path = os.path.join(root_source, html_static_path)
    if not os.path.exists(html_static_path):
        raise FileNotFoundError("no static path:" + html_static_path)
    html_static_paths.append(html_static_path)
    build_paths.append(
        os.path.normpath(os.path.join(html_static_path, "..", "..", "build", "html")))
    custom_latex_processing = theconf.__dict__.get(
        "custom_latex_processing", None)
    if custom_latex_processing is not None:
        try:
            res = custom_latex_processing("dummy phrase")
            if res is None:
                raise ValueError("result should be None")
        except ValueError as e:
            pass

    ####################################
    # modifies the version number in conf.py
    ####################################
    shutil.copy(os.path.join(root, "README.rst"), root_source)
    shutil.copy(os.path.join(root, "LICENSE.txt"), root_source)

    ##########
    # language
    ##########
    language = theconf.__dict__.get("language", "en")
    use_sys = theconf.__dict__.get("enable_disabled_parts", None)
    latex_book = theconf.__dict__.get('latex_book', False)
    nbexamples_conf = theconf.__dict__.get('example_gallery_config', None)
    # examples_conf = theconf.__dict__.get('sphinx_gallery_conf', None)

    ospath = os.environ["PATH"]
    latex_path = theconf.__dict__.get("latex_path", find_latex_path())
    # graphviz_dot = theconf.__dict__.get("graphviz_dot", find_graphviz_dot())
    pandoc_path = theconf.__dict__.get("pandoc_path", find_pandoc_path())
    if os.path.isfile(latex_path):
        latex_path = os.path.dirname(latex_path)

    ##########
    # nblinks: references for the notebooks, dictionary {(ref, format): link}
    ##########
    nblinks = theconf.__dict__.get("nblinks", None)
    if nblinks is not None and len(nblinks) > 0:
        fLOG("~~~~ NBLINKS - BEGIN")
        for i, (k, v) in enumerate(sorted(nblinks.items())):
            fLOG("     {0}/{1} - '{2}': '{3}'".format(i + 1, len(nblinks), k, v))
        fLOG("~~~~ NBLINKS - END")

    # add to PATH
    if latex_path not in ospath:
        os.environ["PATH"] += ";" + latex_path
    if pandoc_path not in ospath:
        os.environ["PATH"] += ";" + pandoc_path

    #########
    # changes
    #########
    chan = os.path.join(root, "_doc", "sphinxdoc", "source", "filechanges.rst")
    if "modify_commit" in theconf.__dict__:
        modify_commit = theconf.modify_commit
    else:
        modify_commit = None
    generate_changes_repo(
        chan, root, filter_commit=filter_commit, exception_if_empty=from_repo,
        fLOG=fLOG, modify_commit=modify_commit)

    ######################################
    # we copy javascript dependencies, reveal.js
    ######################################
    fLOG("~~~~ JAVASCRIPT:", html_static_paths)
    fLOG("~~~~ ROOT:", root_sphinxdoc)
    fLOG("~~~~ BUILD:", build_paths)
    for html_static_path in html_static_paths:
        install_javascript_tools(
            root_sphinxdoc, dest=html_static_path, fLOG=fLOG)

    ############################
    # we copy the extended styles (notebook, snippets)
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
    try:

        prepare_file_for_sphinx_help_generation({}, root,
                                                os.path.join(
                                                    root, "_doc", "sphinxdoc", "source"),
                                                subfolders=[
                                                    ("src/" + module_name, module_name), ],
                                                silent=True,
                                                rootrep=("_doc.sphinxdoc.source.%s." % (
                                                    module_name,), ""),
                                                optional_dirs=optional_dirs, mapped_function=mapped_function,
                                                replace_relative_import=False, module_name=module_name,
                                                copy_add_ext=copy_add_ext, use_sys=use_sys,
                                                fLOG=fLOG)

    except ImportErrorHelpGen as e:

        fLOG(
            "~~~~ major failure, no solution found yet, please run again the script")
        fLOG("~~~~ list of added modules:")
        remove = [k for k in sys.modules if k not in sys_modules]
        for k in sorted(remove):
            fLOG("~~~~    ", k)

        raise e

    fLOG("~~~~ end of prepare_file_for_sphinx_help_generation")

    ######
    # blog
    ######
    fLOG("~~~~ begin blogs")
    blog_fold = os.path.join(
        os.path.join(root, "_doc/sphinxdoc/source", "blog"))

    if os.path.exists(blog_fold):
        fLOG("    BlogPostList")
        plist = BlogPostList(blog_fold, language=language, fLOG=fLOG)
        fLOG("    BlogPostList.write_aggregated")
        plist.write_aggregated(blog_fold,
                               blog_title=theconf.__dict__.get(
                                   "blog_title", project_var_name),
                               blog_description=theconf.__dict__.get(
                                   "blog_description", "blog associated to " + project_var_name),
                               blog_root=theconf.__dict__.get("blog_root", "__BLOG_ROOT__"))
    else:
        plist = None

    fLOG("~~~~ end blogs")

    ###########
    # notebooks
    ###########
    fLOG("~~~~ begin notebooks")
    indextxtnote = None
    indexlistnote = []
    notebook_dir = os.path.abspath(os.path.join(root, "_doc", "notebooks"))
    notebook_doc = os.path.abspath(
        os.path.join(root, "_doc", "sphinxdoc", "source", "notebooks"))
    if os.path.exists(notebook_dir):
        notebooks = explore_folder(
            notebook_dir, pattern=".*[.]ipynb", fullname=True)[1]
        notebooks = [_ for _ in notebooks if "checkpoint" not in _]
        if len(notebooks) > 0:
            fLOG("*******************************************")
            fLOG("**** notebooks", nbformats)
            fLOG("*******************************************")
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
                                        pandoc_path=pandoc_path, fLOG=fLOG, nblinks=nblinks)
            nbs_all = set(_[0]
                          for _ in nbs_all if os.path.splitext(_[0])[-1] == ".rst")
            if len(nbs_all) != len(indexlistnote):
                ext1 = "nbs_all:\n{0}".format("\n".join(nbs_all))
                ext2 = "indexlistnote:\n{0}".format(
                    "\n".join(str(_) for _ in indexlistnote))
                raise ValueError("Different lengths {0} != {1}\n{2}\n{3}".format(
                    len(nbs_all), len(indexlistnote), ext1, ext2))
            nbs = indexlistnote
            fLOG("*******NB, add:", len(nbs))
            nbs.sort()
            build_notebooks_gallery(nbs, os.path.join(
                notebook_doc, "..", "all_notebooks.rst"), fLOG=fLOG)

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

    fLOG("~~~~ end notebooks")

    #############################################
    # replace placeholder as blog posts list into tocs files
    #############################################
    fLOG("~~~~ blog placeholder")
    if plist is not None:
        replace_placeholder_by_recent_blogpost(
            all_tocs, plist, "__INSERT__", fLOG=fLOG)

    #################################
    #  run the documentation generation
    #################################
    fLOG("~~~~ prepare for SPHINX")
    temp = os.environ["PATH"]
    pyts = get_executables_path()
    sepj = ";" if sys.platform.startswith("win") else ":"
    script = sepj.join(pyts)
    fLOG("adding " + script)
    temp = script + sepj + temp
    os.environ["PATH"] = temp
    fLOG("~~~~ changing PATH", temp)
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
    fLOG("~~~~ checking encoding utf8...")
    for root, dirs, files in os.walk(docpath):
        for name in files:
            thn = os.path.join(root, name)
            if name.endswith(".rst"):
                try:
                    with open(thn, "r", encoding="utf8") as f:
                        f.read()
                except UnicodeDecodeError as e:
                    raise HelpGenException(
                        "issue with encoding in a file", thn) from e
                except Exception as e:
                    raise HelpGenException("issue with file ", thn) from e

                # to avoid an error later
                with open(thn, 'r') as f:
                    try:
                        f.read().splitlines()
                    except UnicodeDecodeError as e:
                        warnings.warn(
                            "*** potential issue with encoding for file " + thn + "\n" + str(e))
                    except Exception as e:
                        raise HelpGenException(
                            "issue with file ", thn) from e

    fLOG("~~~~ running sphinx... from", docpath)
    if not os.path.exists(docpath):
        raise FileNotFoundError(docpath)

    os.chdir(docpath)

    #####################
    # builds command lines
    #####################
    fLOG("~~~~ sphinx command lines")
    cmds = []
    lays = []
    cmds_post = []
    for t3 in layout:
        lay, build, override, newconf = lay_build_override_newconf(t3)

        if lay == "pdf":
            lay = "latex"

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

        cmd = ["sphinx-build", "-j", "2", "-v", "-T", "-b", "{0}".format(lay),
               "-d", "{0}/doctrees".format(build)] + over + sconf + ["source", "{0}/{1}".format(build, lay)]
        cmds.append((cmd, build, lay))
        fLOG("~~~~ run:", cmd)
        lays.append(lay)

        if add_htmlhelp and lay == "html":
            # we cannot execute htmlhelp in the same folder
            # as it changes the encoding
            cmd = ["sphinx-build", "-j", "2", "-v", "-T", "-b", "{0}help".format(lay),
                   "-d", "{0}/doctrees".format(build)] + over + sconf + ["source", "{0}/{1}html".format(build, lay)]
            cmds.append((cmd, build, "add_htmlhelp"))
            fLOG("~~~~ run:", cmd)
            lays.append(lay)
            hhp = os.path.join(build, lay + "help", module_name + "_doc.hhp")
            cmdp = '"C:\\Program Files (x86)\\HTML Help Workshop\\hhc.exe" ' + \
                '"%s"' % hhp
            cmds_post.append(cmdp)

    # cmd = "make {0}".format(lay)

    ###############################################################
    # run cmds (prefer to use os.system instread of run_cmd if it gets stuck)
    ###############################################################
    fLOG("~~~~ RUN SPHINX")
    for cmd, build, kind in cmds:
        fLOG(
            "##################################################################################################")
        fLOG(
            "##################### run sphinx #################################################################")
        fLOG(
            "##################################################################################################")
        fLOG("~~~~", cmd)
        fLOG("~~~~ from ", os.getcwd())
        fLOG("~~~~ PATH ", os.environ["PATH"])

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
                           'sphinxcontrib', 'zmq', 'nbformat', 'nbpresent', 'nbconvert',
                           'encodings', 'entrypoints', 'html', 'ipykernel', 'isodate',
                           'jsonschema', 'jupyter_client', 'mistune', 'nbbrowserpdf',
                           'notebook', 'pyparsing', 'zmq', 'jupyter_core',
                           'timeit', 'sphinxcontrib_images_lightbox2', 'win32con'):
                    if ex == pr or ex.startswith(pr + "."):
                        doesrem = False
            else:
                doesrem = False
            if doesrem:
                fLOG("remove '{0}' from sys.modules".format(ex))
                del sys.modules[ex]

        fLOG(
            "##################################################################################################")

        # direct call
        if direct_call:
            # mostly to debug
            out = StringIO()
            err = StringIO()
            memo_out = sys.stdout
            memo_err = sys.stderr
            sys.stdout = out
            sys.stderr = out
            build_main(cmd)
            sys.stdout = memo_out
            sys.stderr = memo_err
            out = out.getvalue()
            err = err.getvalue()
        else:
            out, err = _process_sphinx_in_private_cmd(cmd, fLOG=fLOG)

        if len(err) > 0:
            if "Exception occurred:" in err:
                raise HelpGenException(
                    "Sphinx raised an exception:\nOUT:\n{0}\nERR:\n{1}".format(out, err))
            else:
                fLOG("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                fLOG("~~~~", kind, "~~~~", cmd)
                fLOG("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                warnings.warn(
                    "Sphinx went through errors. Check if any of them is important.\nOUT:\n{0}\nERR:\n{1}".format(out, err))
                fLOG("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                fLOG("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

        if kind == "html":
            fLOG(
                "##############################################################")
            fLOG("check that index.html exists")
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

    # we copy the extended styles (notebook, snippets) (again in build folders)
    # we should not need that
    for build_path in build_paths:
        dest = os.path.join(build_path, "_static", style_figure_notebook[0])
        if not os.path.exists(dest):
            fLOG("    CREATE-CSS2", dest)
            with open(dest, "w", encoding="utf-8") as f:
                f.write(style_figure_notebook[1])

    if add_htmlhelp:
        # we call HtmlHelp
        fLOG("### run HTMLHELP ###########################")
        for cmd in cmds_post:
            fLOG("running", cmd)
            out, err = run_cmd(cmd, wait=True, fLOG=fLOG,
                               communicate=True, timeout=600)
            fLOG(out)
            if len(err) > 0:
                warnings.warn(
                    "Sphinx went through errors. Check if any of them is important.\nOUT:\n{0}\nERR:\n{1}".format(out, err))
        fLOG("### end run HTMLHELP #######################")

    #####################################
    # we copy the coverage files if it is missing
    #####################################
    fLOG("**** copy coverage")
    covfold = os.path.join(docpath, "source", "coverage")
    if os.path.exists(covfold):
        fLOG("## coverage[folder]:", covfold)
        allfiles = os.listdir(covfold)
        allf = [_ for _ in allfiles if _.endswith(".rst")]
        if len(allf) == 0:
            # no rst file --> we copy
            allfiles = [os.path.join(covfold, _) for _ in allfiles]
            allfiles = [_ for _ in allfiles if os.path.isfile(_)]
            for lay in lays:
                layfolder = os.path.join(docpath, build, lay)
                fLOG("## coverage[docpath]:", docpath, " -- ",
                     build, " -- ", lay, " ---- ", layfolder)
                if os.path.exists(layfolder):
                    covbuild = os.path.join(layfolder, "coverage")
                    fLOG("covbuild", covbuild)
                    if not os.path.exists(covbuild):
                        os.mkdir(covbuild)
                    for f in allfiles:
                        fLOG("copy ", f, " to ", covbuild)
                        shutil.copy(f, covbuild)
        else:
            fLOG("## ERROR: coverage files with rst in", covfold)
    else:
        fLOG("## no coverage files", covfold)

    #########################################################
    # we copy javascript dependencies to build _download/javascript
    #########################################################
    # for every layout
    fLOG("[revealjs] JAVASCRIPT: COPY", html_static_paths)
    fLOG("[revealjs] BUILD:", build_paths)
    for subf in ["html", "epub"]:
        for html_static_path, build_path in zip(html_static_paths, build_paths):
            builddoc = os.path.join(build_path, subf, "_downloads")
            if not os.path.exists(builddoc):
                builddoc = os.path.join(build_path, "..", subf, "_downloads")
            if not os.path.exists(builddoc):
                builddoc = os.path.join(build_path, "_downloads")
            if os.path.exists(builddoc):
                # no download, there is probably no notebooks
                # so it is not needed
                fLOG("copy javascript static files from",
                     html_static_path, "to", builddoc)
                copy = synchronize_folder(
                    html_static_path, builddoc, copy_1to2=True, fLOG=fLOG)
                fLOG("javascript", len(copy), "files copied")
            else:
                fLOG("[revealjs] no need, no folder", builddoc)

    ######
    # next
    ######
    fLOG("~~~~ LATEX")
    if "latex" in layout:
        fLOG("~~~~ post_process_latex_output", froot)
        post_process_latex_output(
            froot, False, custom_latex_processing=custom_latex_processing)

    if "pdf" in layout:
        fLOG("~~~~ compile_latex_output_final", froot, "**", latex_path)
        compile_latex_output_final(
            froot, latex_path, False, latex_book=latex_book, fLOG=fLOG,
            custom_latex_processing=custom_latex_processing)

    if "html" in layout:
        nbf = os.path.join(build, "html", "notebooks")
        if os.path.exists(nbf):
            post_process_html_nb_output_static_file(nbf, fLOG=fLOG)
            post_process_html_nb_output_static_file(
                os.path.join(build, "html", "_downloads"), fLOG=fLOG)

    for build_path in build_paths:
        src = os.path.join(build_path, "_images")
        dest = os.path.join(build_path, "_downloads")
        if os.path.exists(src) and os.path.exists(dest):
            fLOG("[imgs] look for images in ", src)
            for img in enumerate_copy_images_for_slides(src, dest):
                fLOG("[imgs]    copy image for slides:", img)

    #####
    # end
    #####
    os.chdir(pa)
    fLOG("################################")
    fLOG("#### END - check log for success")
    fLOG("################################")


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
    fLOG("~~~~~~~~~~~~~~~~~~~~~~~~~~~ _process_sphinx_in_private_cmd BEGIN")
    ok = run_cmd(cmd, wait=True, fLOG=fLOG,
                 communicate=False, tell_if_no_output=120)
    fLOG("~~~~~~~~~~~~~~~~~~~~~~~~~~~ _process_sphinx_in_private_cmd END")
    return ok
