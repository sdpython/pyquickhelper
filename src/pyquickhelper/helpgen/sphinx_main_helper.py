# -*- coding: utf-8 -*-
"""
@file
@brief Contains helpers for the main function @see fn generate_help_sphinx

"""
import os
import sys
import datetime

from ..loghelper.flog import run_cmd, fLOG
from ..loghelper.pyrepo_helper import SourceRepository
from ..pandashelper.tblformat import df2rst
from .utils_sphinx_doc_helpers import HelpGenException
from .post_process import post_process_latex_output

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


def setup_environment_for_help():
    """
    modifies environment variables to be able to use external tools
    such as `Inkscape <https://inkscape.org/>`_

    .. versionadded:: 1.2
    """
    if sys.platform.startswith("win"):
        prog = os.environ["ProgramFiles"]
        inkscape = os.path.join(prog, "Inkscape")
        if not os.path.exists(inkscape):
            raise FileNotFoundError(
                "Inkscape is not installed, expected at: {0}".format(inkscape))
        path = os.environ["PATH"]
        if inkscape not in path:
            fLOG("SETUP: add path to %path%", inkscape)
            os.environ["PATH"] = path + ";" + inkscape
    else:
        pass


def get_executables_path():
    """
    returns the paths to Python, Python Scripts

    @return     a list of paths
    """
    res = [os.path.split(sys.executable)[0]]
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

    # we move pandas here because it imports matplotlib
    # which is not always wise when you need to modify the backend
    import pandas
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
                "unable to retrieve log in " + source + "\n" + str(eee)) from eee
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
        import pandas
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
            out, err = run_cmd(c, wait=True, do_not_log=False,
                               log_error=False, catch_exit=True)
            if len(err) > 0:
                raise HelpGenException(
                    "CMD:\n{0}\nERR:\n{1}\nOUT:\n{2}".format(c, err, out))
            # second compilation
            fLOG("   ** LATEX compilation (d)", c)
            out, err = run_cmd(c, wait=True, do_not_log=False, log_error=False)
            if len(err) > 0:
                raise HelpGenException(err)


def replace_placeholder_by_recent_blogpost(all_tocs, plist, placeholder, nb_post=5):
    """
    replaces a place holder by a list of blog post

    @param      all_tocs        list of files to look into
    @param      plist           list of blog post
    @param      placeholder     place holder to replace
    @param      nb_post         number of blog post to display
    """
    def make_link(post):
        name = os.path.splitext(os.path.split(post.FileName)[-1])[0]
        s = """<a href="{{ pathto('',1) }}/blog/%s/%s.html">%s - %s</a>""" % (
            post.Year, name, post.Date, post.Title)
        return s

    end = min(nb_post, len(plist))
    for toc in all_tocs:
        with open(toc, "r", encoding="utf8") as f:
            content = f.read()
        if placeholder in content:
            fLOG("  *** update", toc)
            links = [make_link(post) for post in plist[:end]]
            content = content.replace(placeholder, "\n<br />".join(links))
            with open(toc, "w", encoding="utf8") as f:
                f.write(content)
