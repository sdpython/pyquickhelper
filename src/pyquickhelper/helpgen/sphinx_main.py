# -*- coding: utf-8 -*-
"""
@file
@brief Contains the main function to generate the documentation
for a module designed the same way as this one, @see fn generate_help_sphinx.

"""
try:
    import pandas
    has_pandas = True
except ImportError:
    has_pandas = False

import os
import sys
import shutil
import datetime
import importlib
import warnings
from docutils.parsers.rst import directives

from ..loghelper.flog import run_cmd, fLOG
from ..loghelper.pyrepo_helper import SourceRepository
from ..pandashelper.tblformat import df2rst
from .utils_sphinx_doc import prepare_file_for_sphinx_help_generation
from .utils_sphinx_doc_helpers import HelpGenException, find_latex_path, find_pandoc_path, ImportErrorHelpGen
from ..filehelper.synchelper import explore_folder
from .utils_sphinx_config import ie_layout_html
from .blog_post_list import BlogPostList
from .sphinx_blog_extension import BlogPostDirective, BlogPostDirectiveAgg
from .post_process import post_process_latex_output
from .process_notebooks import process_notebooks, add_notebook_page
from .sphinx_helper import post_process_html_nb_output_static_file
from .texts_language import TITLES

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
                         extra_ext=[],
                         nbformats=["ipynb", "html", "python", "rst", "pdf"],
                         layout=[("html", "build", {})],
                         module_name=None,
                         from_repo=True,
                         use_run_cmd=False):
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
    @param      extra_ext           list of file extensions (not .py)
    @param      nbformats           requested formats for the notebooks conversion
    @param      layout              list of formats sphinx should generate such as html, latex, pdf, docx,
                                    it is a list of tuple (layout, build directory, parameters to override)
    @param      module_name         name of the module (must be the folder name src/*name*, if None, *module_name*
                                    will be replaced by *project_var_name*
    @param      from_repo           if True, assumes the sources come from a source repository,
                                    False otherwise
    @param      use_run_cmd         use @see fn run_cmd instead os ``os.system`` (default) to run Sphinx

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

    .. versionchanged:: 1.0
        Assumes IPython 3 is installed. It might no work for earlier versions (notebooks).
        Parameters *from_repo*, *use_run_cmd* were added.

    """

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

    if "conf" in sys.modules:
        raise ImportError("module conf was imported, this function expects not to:\n{0}".format(
            sys.modules["conf"].__file__))

    # root_source
    root = os.path.abspath(root)
    froot = root
    root_sphinxdoc = os.path.join(root, "_doc", "sphinxdoc")
    root_source = os.path.join(root_sphinxdoc, "source")

    # we import conf_base, specific to ensae_teaching_cs
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

    # import others conf, we must do it now
    # it takes too long to do ot after if there is an error
    # we assume the configuration are not too different
    # about language for example, latex_path, pandoc_path
    for t3 in layout:
        lay, build, override, newconf = lay_build_override_newconf(t3)
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
        add_missing_files(root, thenewconf)
        del sys.modules["conf"]

    # we add the source path to the list of path to considered before importing
    sys.path.append(root_source)

    # import conf.py
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
    add_missing_files(root, theconf)

    # modifies the version number in conf.py
    shutil.copy(os.path.join(root, "README.rst"), root_source)
    shutil.copy(os.path.join(root, "LICENSE.txt"), root_source)

    # language
    language = theconf.__dict__.get("language", "en")

    latex_path = theconf.__dict__.get("latex_path", find_latex_path())
    # graphviz_dot = theconf.__dict__.get("graphviz_dot", find_graphviz_dot())
    pandoc_path = theconf.__dict__.get("pandoc_path", find_pandoc_path())

    # changes
    chan = os.path.join(root, "_doc", "sphinxdoc", "source", "filechanges.rst")
    generate_changes_repo(
        chan, root, filter_commit=filter_commit, exception_if_empty=from_repo)

    # copy the files
    optional_dirs = []

    mapped_function = [(".*[.]%s$" % ext.strip("."), None)
                       for ext in extra_ext]

    if module_name is None:
        module_name = project_var_name

    # we save the module already imported
    sys_modules = set(sys.modules.keys())

    # generates extra files
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
            module_name=module_name)

    except ImportErrorHelpGen as e:

        fLOG(
            "**** major failure, no solution found yet, please run again the script")
        fLOG("**** list of added modules:")
        remove = [k for k in sys.modules if k not in sys_modules]
        for k in sorted(remove):
            fLOG("****    ", k)

        raise e

    fLOG("**** end of prepare_file_for_sphinx_help_generation")

    # blog
    blog_fold = os.path.join(
        os.path.join(root, "_doc/sphinxdoc/source", "blog"))

    if os.path.exists(blog_fold):
        plist = BlogPostList(blog_fold, language=language)
        plist.write_aggregated(blog_fold,
                               blog_title=theconf.__dict__.get(
                                   "blog_title", project_var_name),
                               blog_description=theconf.__dict__.get(
                                   "blog_description", "blog associated to " + project_var_name),
                               blog_root=theconf.__dict__.get("blog_root", "__BLOG_ROOT__"))

    # notebooks
    notebook_dir = os.path.abspath(os.path.join(root, "_doc", "notebooks"))
    notebook_doc = os.path.abspath(
        os.path.join(root, "_doc", "sphinxdoc", "source", "notebooks"))
    if os.path.exists(notebook_dir):
        notebooks = explore_folder(
            notebook_dir, pattern=".*[.]ipynb", fullname=True)[1]
        notebooks = [_ for _ in notebooks if "checkpoint" not in _]
        if len(notebooks) > 0:
            fLOG("**** notebooks", nbformats)
            build = os.path.join(root, "build", "notebooks")
            if not os.path.exists(build):
                os.makedirs(build)
            if not os.path.exists(notebook_doc):
                os.mkdir(notebook_doc)
            nbs = process_notebooks(notebooks,
                                    build=build,
                                    outfold=notebook_doc,
                                    formats=nbformats,
                                    latex_path=latex_path,
                                    pandoc_path=pandoc_path)
            nbs = list(set(nbs))
            add_notebook_page(
                nbs, os.path.join(notebook_doc, "..", "all_notebooks.rst"))

        imgs = [os.path.join(notebook_dir, _)
                for _ in os.listdir(notebook_dir) if ".png" in _]
        if len(imgs) > 0:
            for img in imgs:
                shutil.copy(img, notebook_doc)

    #  run the documentation generation
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

    # checks encoding
    fLOG("checking encoding utf8...")
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
                        raise HelpGenException(
                            "issue with encoding for file ", thn) from e
                    except Exception as e:
                        raise HelpGenException(
                            "issue with file (2) ", thn) from e

    fLOG("running sphinx... from", docpath)
    if not os.path.exists(docpath):
        raise FileNotFoundError(docpath)

    os.chdir(docpath)

    # builds command lines
    cmds = []
    lays = []
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
        cmds.append(cmd)
        fLOG("run:", cmd)
        lays.append(lay)

    # cmd = "make {0}".format(lay)

    # run cmds (prefer to use os.system instread of run_cmd if it gets stuck)
    for cmd in cmds:
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
        fLOG(
            "##################################################################################################")
        fLOG(
            "##################### end run sphinx #############################################################")
        fLOG(
            "##################################################################################################")

    # we copy the coverage files if it is missing
    covfold = os.path.join(docpath, "source", "coverage")
    if os.path.exists(covfold):
        fLOG("## coverage folder:", covfold)
        allfiles = os.listdir(covfold)
        allf = [_ for _ in allfiles if _.endswith(".rst")]
        if len(allf) == 0:
            # no rst file --> we copy
            allfiles = [os.path.join(covfold, _) for _ in allfiles]
            for lay in lays:
                layfolder = os.path.join(docpath, build, lay)
                fLOG("## docpath:", docpath, " -- ", build, " -- ", lay)
                if os.path.exists(layfolder):
                    covbuild = os.path.join(docpath, build, lay, "coverage")
                    fLOG("covbuild", covbuild)
                    if not os.path.exists(covbuild):
                        os.mkdir(covbuild)
                    for f in allfiles:
                        fLOG("copy ", f, " to ", covbuild)
                        shutil.copy(f, covbuild)
    else:
        fLOG("## no coverage files", covfold)

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

    # end
    os.chdir(pa)


def add_missing_files(root, conf):
    """
    add missing files for the documentation,
    ``moduletoc.html``, ``blogtoc.html``

    @param      root        root
    @param      conf        configuration module (to guess the template folder)
    """
    fold = conf.templates_path
    if isinstance(fold, list):
        fold = fold[0]

    if hasattr(conf, "language"):
        language = conf.language
    else:
        language = "en"

    loc = os.path.join(root, "_doc", "sphinxdoc", "source", fold)
    if not os.path.exists(loc):
        os.makedirs(loc)

    # moduletoc.html
    mt = os.path.join(loc, "moduletoc.html")
    if not os.path.exists(mt):
        with open(mt, "w", encoding="utf8") as f:
            f.write(
                """<h3><a href="{{ pathto(master_doc) }}">{{ _('%s') }}</a></h3>\n""" % TITLES[language]["toc"])
            f.write("""{{ toctree() }}""")

    # blogtoc.html
    mt = os.path.join(loc, "blogtoc.html")
    if not os.path.exists(mt):
        with open(mt, "w", encoding="utf8") as f:
            f.write(
                """<h3><a href="{{ pathto(master_doc) }}">{{ _('Blog') }}</a></h3>\n""")
            f.write("""{{ toctree() }}""")


def get_executables_path():
    """
    returns the paths to Python, Python Scripts

    @return     a list of paths
    """
    res = [os.path.split(sys.executable)[0]]
    if sys.platform.startswith("win"):
        res += [os.path.join(res[-1], "Scripts")]
        ver = "c:\\Python%d%d" % (
            sys.version_info.major, sys.version_info.minor)
        res += [ver]
        res += [os.path.join(res[-1], "Scripts")]

    return res


def my_date_conversion(sdate):
    """
    converts a date into a datetime

    @param      sdate       string
    @return                 date

    .. versionadded:: 1.0

    """
    first = sdate.split(" ")[0]
    trois = first.replace(".", "-").replace("/", "-").split("-")
    return datetime.datetime(int(trois[0]), int(trois[1]), int(trois[2]))


def produce_code_graph_changes(df):
    """
    return the code for a graph which counts the number of changes per week over the last year

    @param      df      dataframe (has a column date with format ``YYYY-MM-DD``)
    @return             graph

    .. versionchanged:: 1.0
        The call to `datetime.datetime.strptime <https://docs.python.org/3.4/library/datetime.html#strftime-strptime-behavior>`_
        introduced exceptions::

            File "<frozen importlib._bootstrap>", line 2212, in _find_and_load_unlocked
            File "<frozen importlib._bootstrap>", line 321, in _call_with_frames_removed
            File "<frozen importlib._bootstrap>", line 2254, in _gcd_import
            File "<frozen importlib._bootstrap>", line 2237, in _find_and_load
            File "<frozen importlib._bootstrap>", line 2224, in _find_and_load_unlocked

        when generating the documentation for another project. The reason
        is still unclear. It was replaced by a custom function.

    """
    def to_dt(x):
        return datetime.datetime(x.year, x.month, x.day)

    def year_week(x):
        dt = datetime.datetime(x.year, x.month, x.day)
        return dt.isocalendar()[:2]

    def to_str(x):
        year, week = year_week(x)
        return "%d-w%02d" % (year, week)

    df = df.copy()
    df["dt"] = df.apply(lambda r: my_date_conversion(r["date"]), axis=1)
    df = df[["dt"]]
    now = datetime.datetime.now()
    last = now - datetime.timedelta(365)
    df = df[df.dt >= last]
    df["week"] = df.apply(lambda r: to_str(r["dt"]), axis=1)
    df["commits"] = 1

    val = []
    for alldays in range(0, 365):
        a = now - datetime.timedelta(alldays)
        val.append({"dt": a, "week": to_str(a), "commits": 0})

    df = pandas.concat([df, pandas.DataFrame(val)])

    gr = df[["week", "commits"]].groupby("week", as_index=False).sum()
    xl = list(gr["week"])
    x = list(range(len(xl)))
    y = list(gr["commits"])

    typstr = str  # unicode#

    code = """
            import matplotlib.pyplot as plt
            x = __X__
            y = __Y__
            xl = __XL__
            plt.close('all')
            plt.style.use('ggplot')
            fig,ax = plt.subplots(nrows=1,ncols=1,figsize=(10,4))
            ax.bar( x,y )
            tig = ax.get_xticks()
            labs = [ ]
            for t in tig:
                if t in x: labs.append(xl[x.index(t)])
                else: labs.append("")
            ax.set_xticklabels( labs )
            ax.grid(True)
            ax.set_title("commits")
            plt.show()
            """.replace("            ", "") \
               .replace("__X__", typstr(x)) \
               .replace("__XL__", typstr(xl)) \
               .replace("__Y__", typstr(y))

    return code


def generate_changes_repo(chan,
                          source,
                          exception_if_empty=True,
                          filter_commit=lambda c: c.strip() != "documentation"):
    """
    Generates a rst tables containing the changes stored by a svn or git repository,
    the outcome is stored in a file.
    The log comment must start with ``*`` to be taken into account.

    @param          chan                filename to write (or None if you don't need to)
    @param          source              source folder to get changes for
    @param          exception_if_empty  raises an exception if empty
    @param          filter_commit       function which accepts a commit to show on the documentation (based on the comment)
    @return                             string (rst tables with the changes)

    .. versionchanged:: 1.0

        pandas is not imported in the function itself but at the beginning of the module. It
        seemed to cause soe weird exceptions when generating the documentation for another module::

            File "<frozen importlib._bootstrap>", line 2212, in _find_and_load_unlocked
            File "<frozen importlib._bootstrap>", line 321, in _call_with_frames_removed
            File "<frozen importlib._bootstrap>", line 2254, in _gcd_import
            File "<frozen importlib._bootstrap>", line 2237, in _find_and_load
            File "<frozen importlib._bootstrap>", line 2224, in _find_and_load_unlocked

        Doing that helps. The cause still remains obscure.

    """
    # builds the changes files
    try:
        src = SourceRepository(commandline=True)
        logs = src.log(path=source)
    except Exception as eee:
        if exception_if_empty:
            fLOG("error, unable to retrieve log from " + source)
            raise HelpGenException(
                "unable to retrieve log in " + source) from eee
        else:
            logs = [("none", 0, datetime.datetime.now(), "-")]
            fLOG("error,", eee)

    if len(logs) == 0:
        fLOG("error, unable to retrieve log from " + source)
        if exception_if_empty:
            raise HelpGenException("retrieved logs are empty in " + source)
    else:
        fLOG("info, retrieved ", len(logs), " commits")

    rows = []
    rows.append(
        """\n.. _l-changes:\n\n\nChanges\n=======\n\n__CODEGRAPH__\n\nList of recent changes:\n""")

    typstr = str  # unicode#

    values = []
    for i, row in enumerate(logs):
        n = len(logs) - i
        code, nbch, date, comment = row[:4]
        last = row[-1]
        if last.startswith("http"):
            nbch = "`%s <%s>`_" % (typstr(nbch), last)

        ds = "%04d-%02d-%02d" % (date.year, date.month, date.day)
        if filter_commit(comment):
            if isinstance(nbch, int):
                values.append(
                    ["%d" % n, "%04d" % nbch, "%s" % ds, comment.strip("*")])
            else:
                values.append(
                    ["%d" % n, "%s" % nbch, "%s" % ds, comment.strip("*")])

    if len(values) == 0 and exception_if_empty:
        raise HelpGenException(
            "Logs were not empty but there was no comment starting with '*' from " + source + "\n" + "\n".join([typstr(_) for _ in logs]))

    if len(values) > 0:
        tbl = pandas.DataFrame(
            columns=["#", "change number", "date", "comment"], data=values)
        rows.append(
            "\n\n" + df2rst(tbl, align=["1x", "1x", "1x", "3x"]) + "\n\n")

    final = "\n".join(rows)

    if len(values) > 0:
        code = produce_code_graph_changes(tbl)
        code = code.split("\n")
        code = ["    " + _ for _ in code]
        code = "\n".join(code)
        code = ".. plot::\n" + code + "\n"
        final = final.replace("__CODEGRAPH__", code)

    if chan is not None:
        with open(chan, "w", encoding="utf8") as f:
            f.write(final)
    return final


def compile_latex_output_final(root, latex_path, doall, afile=None):
    """
    compiles the latex documents

    @param      root        root
    @param      latex_path  path to the compiler
    @param      doall       do more transformation of the latex file before compiling it
    @param      afile       process a specific file
    """
    if sys.platform.startswith("win"):
        lat = os.path.join(latex_path, "pdflatex.exe")
    else:
        lat = "pdflatex"

    build = os.path.join(root, "_doc", "sphinxdoc", "build", "latex")
    for tex in os.listdir(build):
        if tex.endswith(".tex") and (afile is None or afile in tex):
            file = os.path.join(build, tex)
            if doall:
                # -interaction=batchmode
                c = '"{0}" "{1}" -output-directory="{2}"'.format(
                    lat, file, build)
            else:
                c = '"{0}" "{1}" -interaction=batchmode -output-directory="{2}"'.format(
                    lat, file, build)
            fLOG("   ** LATEX compilation (c)", c)
            post_process_latex_output(file, doall)
            out, err = run_cmd(c, wait=True, do_not_log=False, log_error=False)
            if len(err) > 0:
                raise HelpGenException(
                    "CMD:\n{0}\nERR:\n{1}\nOUT:\n{2}".format(c, err, out))
            # second compilation
            fLOG("   ** LATEX compilation (d)", c)
            out, err = run_cmd(c, wait=True, do_not_log=False, log_error=False)
            if len(err) > 0:
                raise HelpGenException(err)
