# -*- coding: utf-8 -*-
"""
@file
@brief Contains the main function to generate the documentation
for a module designed the same way as this one, @see fn generate_help_sphinx.

"""
import os
import sys
import shutil
import importlib
import warnings
from docutils.parsers.rst import directives, roles

from ..loghelper.flog import run_cmd, fLOG
from .utils_sphinx_doc import prepare_file_for_sphinx_help_generation
from .utils_sphinx_doc_helpers import HelpGenException, ImportErrorHelpGen
from .conf_path_tools import find_latex_path, find_pandoc_path
from ..filehelper.synchelper import explore_folder
from .utils_sphinx_config import ie_layout_html
from .blog_post_list import BlogPostList
from .sphinx_blog_extension import BlogPostDirective, BlogPostDirectiveAgg
from .sphinx_runpython_extension import RunPythonDirective
from .sphinx_sharenet_extension import ShareNetDirective, sharenet_role
from .sphinx_bigger_extension import bigger_role
from .post_process import post_process_latex_output
from .process_notebooks import process_notebooks, add_notebook_page
from .sphinx_helper import post_process_html_nb_output_static_file
from .install_js_dep import install_javascript_tools
from ..filehelper import synchronize_folder
from .sphinx_main_helper import setup_environment_for_help, get_executables_path, generate_changes_repo, compile_latex_output_final, replace_placeholder_by_recent_blogpost
from .sphinx_main_verification import verification_html_format
from .sphinx_main_missing_html_files import add_missing_files


if sys.version_info[0] == 2:
    from codecs import open

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


def generate_help_sphinx(project_var_name,
                         clean=True,
                         root=".",
                         filter_commit=lambda c: c.strip() != "documentation",
                         extra_ext=None,
                         nbformats=[
                             "ipynb", "html", "python", "rst", "slides", "pdf"],
                         layout=[("html", "build", {}), ("epub", "build", {})],
                         module_name=None,
                         from_repo=True,
                         use_run_cmd=False,
                         add_htmlhelp=False,
                         copy_add_ext=None,
                         fLOG=fLOG):
    """
    runs the help generation
        - copies every file in another folder
        - replaces comments in doxygen format into rst format
        - replaces local import by global import (tweaking sys.path too)
        - calls sphinx to generate the documentation.

    @param      project_var_name    project name
    @param      clean               if True, cleans the previous documentation first, does not work on linux yet
    @param      root                see below
    @param      filter_commit       function which accepts a commit to show on the documentation (based on the comment)
    @param      extra_ext           list of file extensions to document (not .py)
    @param      nbformats           requested formats for the notebooks conversion
    @param      layout              list of formats sphinx should generate such as html, latex, pdf, docx,
                                    it is a list of tuple (layout, build directory, parameters to override)
    @param      module_name         name of the module (must be the folder name src/*name*, if None, *module_name*
                                    will be replaced by *project_var_name*
    @param      from_repo           if True, assumes the sources come from a source repository,
                                    False otherwise
    @param      use_run_cmd         use @see fn run_cmd instead os ``os.system`` (default) to run Sphinx
    @param      add_htmlhelp        run HTML Help too (only on Windows)
    @param      copy_add_ext        additional file extension to copy
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

    @example(run help generation)
    @code
    # from the main folder which contains folder src
    generate_help_sphinx("pyquickhelper")
    @endcode
    @endexample

    .. index:: extension, extra extension, ext

    By default, the function only consider files end by ``.py`` and ``.rst`` but you could
    add other files sharing the same extensions by adding this one
    in the ``extra_ext`` list.

    @example(other page of examples___run help generation)
    This example is exactly the same as the previous one but will be generated on another page of examples.
    @code
    # from the main folder which contains folder src
    generate_help_sphinx("pyquickhelper")
    @endcode
    @endexample

    @example(page with an accent -é- in the title___run help generation)
    Same page with an accent.
    @code
    # from the main folder which contains folder src
    generate_help_sphinx("pyquickhelper")
    @endcode
    @endexample

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
    """
    setup_environment_for_help()

    if add_htmlhelp:
        if not sys.platform.startswith("win"):
            raise ValueError("add_htmlhelp is True and the OS is not Windows")
        else:
            fLOG("add add_htmlhelp")

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

    ie_layout_html()

    directives.register_directive("blogpost", BlogPostDirective)
    directives.register_directive("blogpostagg", BlogPostDirectiveAgg)
    directives.register_directive("runpython", RunPythonDirective)
    directives.register_directive("sharenet", ShareNetDirective)
    roles.register_canonical_role("sharenet", sharenet_role)
    roles.register_canonical_role("bigger", bigger_role)

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

    ###############################################
    # we import conf_base, specific to ensae_teaching_cs
    ###############################################
    confb = os.path.join(root_source, "conf_base.py")
    if os.path.exists(confb):
        try:
            import conf_base
        except ImportError as e:
            sys.path.append(root_source)
            import conf_base
            del sys.path[-1]

        fLOG("conf_base", conf_base.__file__)

    copypath = list(sys.path)

    # stores static path for every layout, we store them to copy
    html_static_paths = []
    build_paths = []
    all_tocs = []

    ###################################
    # import others conf, we must do it now
    # it takes too long to do it after if there is an error
    # we assume the configuration are not too different
    # about language for example, latex_path, pandoc_path
    #################################################
    for t3 in layout:
        lay, build, override, newconf = lay_build_override_newconf(t3)
        build = os.path.normpath(os.path.abspath(build))
        fLOG("newconf:", newconf, t3)
        if newconf is None:
            continue
        # we need to import this file to guess the template directory and
        # add missing templates
        folds = os.path.join(root_sphinxdoc, newconf)
        # trick, we place the good folder in the first position
        sys.path.insert(0, folds)
        fLOG("import from", folds)
        try:
            thenewconf = importlib.import_module("conf")
            fLOG("import:", thenewconf)
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

        # we store the html_static_path in html_static_paths
        html_static_path = thenewconf.__dict__.get(
            "html_static_path", "phdoc_static")
        if isinstance(html_static_path, list):
            html_static_path = html_static_path[0]
        html_static_path = os.path.join(root_source, html_static_path)
        if not os.path.exists(html_static_path):
            raise FileNotFoundError("no static path:" + html_static_path)
        html_static_paths.append(html_static_path)
        build_paths.append(build)

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

    latex_path = theconf.__dict__.get("latex_path", find_latex_path())
    # graphviz_dot = theconf.__dict__.get("graphviz_dot", find_graphviz_dot())
    pandoc_path = theconf.__dict__.get("pandoc_path", find_pandoc_path())
    if os.path.isfile(latex_path):
        latex_path = os.path.dirname(latex_path)

    #########
    # changes
    #########
    chan = os.path.join(root, "_doc", "sphinxdoc", "source", "filechanges.rst")
    generate_changes_repo(
        chan, root, filter_commit=filter_commit, exception_if_empty=from_repo)

    ######################################
    # we copy javascript dependencies, reveal.js
    ######################################
    fLOG("JAVASCRIPT:", html_static_paths)
    fLOG("BUILD:", build_paths)
    for html_static_path in html_static_paths:
        install_javascript_tools(
            root_sphinxdoc, dest=html_static_path, fLOG=fLOG)

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

        prepare_file_for_sphinx_help_generation(
            {},
            root,
            os.path.join(root, "_doc", "sphinxdoc", "source"),
            subfolders=[
                ("src/" + module_name, module_name),
            ],
            silent=True,
            rootrep=("_doc.sphinxdoc.source.%s." % (module_name,), ""),
            optional_dirs=optional_dirs,
            mapped_function=mapped_function,
            replace_relative_import=False,
            module_name=module_name,
            copy_add_ext=copy_add_ext,
            use_sys=use_sys,
            fLOG=fLOG)

    except ImportErrorHelpGen as e:

        fLOG(
            "**** major failure, no solution found yet, please run again the script")
        fLOG("**** list of added modules:")
        remove = [k for k in sys.modules if k not in sys_modules]
        for k in sorted(remove):
            fLOG("****    ", k)

        raise e

    fLOG("**** end of prepare_file_for_sphinx_help_generation")

    ######
    # blog
    ######
    fLOG("**** begin blogs")
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

    fLOG("**** end blogs")

    ###########
    # notebooks
    ###########
    fLOG("**** begin notebooks")
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
            if not os.path.exists(notebook_doc):
                os.mkdir(notebook_doc)
            nbs_all = process_notebooks(notebooks,
                                        build=build,
                                        outfold=notebook_doc,
                                        formats=nbformats,
                                        latex_path=latex_path,
                                        pandoc_path=pandoc_path)
            nbs = list(set(_[0] for _ in nbs_all))
            fLOG("*******NB, add:", nbs)
            add_notebook_page(
                nbs, os.path.join(notebook_doc, "..", "all_notebooks.rst"))

        imgs = [os.path.join(notebook_dir, _)
                for _ in os.listdir(notebook_dir) if ".png" in _]
        if len(imgs) > 0:
            for img in imgs:
                shutil.copy(img, notebook_doc)

    fLOG("**** end notebooks")

    #############################################
    # replace placeholder as blog posts list into tocs files
    #############################################
    fLOG("**** blog placeholder")
    if plist is not None:
        replace_placeholder_by_recent_blogpost(all_tocs, plist, "__INSERT__")

    #################################
    #  run the documentation generation
    #################################
    fLOG("**** prepare for SPHINX")
    temp = os.environ["PATH"]
    pyts = get_executables_path()
    sepj = ";" if sys.platform.startswith("win") else ":"
    script = sepj.join(pyts)
    fLOG("adding " + script)
    temp = script + sepj + temp
    os.environ["PATH"] = temp
    fLOG("changing PATH", temp)
    pa = os.getcwd()

    thispath = os.path.normpath(root)
    docpath = os.path.normpath(os.path.join(thispath, "_doc", "sphinxdoc"))

    ################
    # checks encoding
    ################
    fLOG("**** checking encoding utf8...")
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

    fLOG("running sphinx... from", docpath)
    if not os.path.exists(docpath):
        raise FileNotFoundError(docpath)

    os.chdir(docpath)

    #####################
    # builds command lines
    #####################
    fLOG("**** sphinx command lines")
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
                    cmd = "rmdir /q /s {0}\\{1}".format(build, fold)
                    run_cmd(cmd, wait=True)
            cmd = r"del /q /s {0}\*".format(build)
            run_cmd(cmd, wait=True)

        over = [" -D {0}={1}".format(k, v) for k, v in override.items()]
        over = "".join(over)

        sconf = "" if newconf is None else " -c {0}".format(newconf)

        cmd = "sphinx-build -b {1} -d {0}/doctrees{2}{3} source {0}/{1}".format(
            build, lay, over, sconf)
        cmds.append((cmd, build, lay))
        fLOG("run:", cmd)
        lays.append(lay)

        if add_htmlhelp and lay == "html":
            # we cannot execute htmlhelp in the same folder
            # as it changes the encoding
            cmd = "sphinx-build -b {1}help -d {0}/doctrees{2}{3} source {0}/{1}help".format(
                build, lay, over, sconf)
            cmds.append((cmd, build, "add_htmlhelp"))
            fLOG("run:", cmd)
            lays.append(lay)
            hhp = os.path.join(build, lay + "help", module_name + "_doc.hhp")
            cmdp = '"C:\\Program Files (x86)\\HTML Help Workshop\\hhc.exe" ' + \
                '"%s"' % hhp
            cmds_post.append(cmdp)

    # cmd = "make {0}".format(lay)

    ###############################################################
    # run cmds (prefer to use os.system instread of run_cmd if it gets stuck)
    ###############################################################
    fLOG("**** RUN SPHINX")
    for cmd, build, kind in cmds:
        fLOG(
            "##################################################################################################")
        fLOG(
            "##################### run sphinx #################################################################")
        fLOG(
            "##################################################################################################")
        fLOG("#####", cmd)
        fLOG("##### from ", os.getcwd())
        fLOG("##### PATH ", os.environ["PATH"])
        if use_run_cmd:
            out, err = run_cmd(cmd, wait=True, fLOG=fLOG)
            fLOG(out)
            if len(err) > 0:
                warnings.warn(
                    "Sphinx went through errors. Check if any of them is important.\nOUT:\n{0}\nERR:\n{1}".format(out, err))
        else:
            os.system(cmd)
            out, err = "unknown", "unknown"

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

    if add_htmlhelp:
        # we call HtmlHelp
        fLOG("### run HTMLHELP ###########################")
        for cmd in cmds_post:
            fLOG("running", cmd)
            out, err = run_cmd(cmd, wait=True, fLOG=fLOG)
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
    for html_static_path, build_path in zip(html_static_paths, build_paths):
        builddoc = os.path.join(build_path, "_downloads")
        if os.path.exists(builddoc):
            # no download, there is probably no notebooks
            # so it is not needed
            fLOG("copy javascript static files from",
                 html_static_path, "to", builddoc)
            copy = synchronize_folder(
                html_static_path, builddoc, copy_1to2=True)
            fLOG("javascript", len(copy), "files copied")
        else:
            fLOG("[revealjs] no need, no folder", builddoc)

    ######
    # next
    ######
    fLOG("**** LATEX")
    if "latex" in lays:
        fLOG("---- post_process_latex_output", froot)
        post_process_latex_output(froot, False)

    if "pdf" in layout:
        fLOG("---- compile_latex_output_final", froot, "**", latex_path)
        compile_latex_output_final(froot, latex_path, False)

    if "html" in layout:
        nbf = os.path.join(build, "html", "notebooks")
        if os.path.exists(nbf):
            post_process_html_nb_output_static_file(nbf, fLOG=fLOG)
            post_process_html_nb_output_static_file(
                os.path.join(build, "html", "_downloads"), fLOG=fLOG)

    #####
    # end
    #####
    os.chdir(pa)
    fLOG("################################")
    fLOG("#### END - check log for success")
    fLOG("################################")
